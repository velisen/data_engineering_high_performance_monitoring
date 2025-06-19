import org.apache.kafka.clients.admin.*;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;

public class Main {
    private static final Logger logger = LoggerFactory.getLogger(Main.class);
    private static final String KAFKA_BROKERS = System.getenv().getOrDefault("KAFKA_BROKERS", "localhost:29092,localhost:39092,localhost:49092");
    private static final int NUM_PARTITIONS = 5;
    private static final short REPLICATION_FACTOR = 3;
    private static final String TOPIC_NAME = "FINANCIAL_TRANSACTIONS";

    public static void main(String[] args) throws Exception {
        createTopic(TOPIC_NAME);
        for (int i = 0; i < 3; i++) {
            int threadId = i;
            new Thread(() -> produceTransactions(threadId)).start();
        }
    }

    private static void createTopic(String topicName) {
        Properties props = new Properties();
        props.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, KAFKA_BROKERS);
        try (AdminClient admin = AdminClient.create(props)) {
            Set<String> topics = admin.listTopics().names().get(10, TimeUnit.SECONDS);
            if (!topics.contains(topicName)) {
                NewTopic newTopic = new NewTopic(topicName, NUM_PARTITIONS, REPLICATION_FACTOR);
                admin.createTopics(Collections.singleton(newTopic)).all().get();
                logger.info("Topic '{}' created successfully.", topicName);
            } else {
                logger.info("Topic '{}' already exists.", topicName);
            }
        } catch (Exception e) {
            logger.error("Error creating topic: {}", e.getMessage(), e);
        }
    }    private static void produceTransactions(int threadId) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KAFKA_BROKERS);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "1");
        props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "gzip");
        props.put(ProducerConfig.LINGER_MS_CONFIG, "5");  // Reduced linger time
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 16384);  // Increased batch size
        props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 512000 * 1024L);
        // Add performance-related configs
        props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);
        props.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120000);
        props.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, 30000);

        long messageCount = 0;
        long lastLog = System.currentTimeMillis();
        com.google.gson.Gson gson = new com.google.gson.Gson(); // Create once

        try (KafkaProducer<String, String> producer = new KafkaProducer<>(props)) {
            while (true) {
                Map<String, Object> transaction = generateTransaction();
                String key = (String) transaction.get("user_id");
                String value = gson.toJson(transaction);
                ProducerRecord<String, String> record = new ProducerRecord<>(TOPIC_NAME, key, value);
                
                producer.send(record, (metadata, exception) -> {
                    if (exception != null) {
                        logger.error("Delivery failed: {}", exception.getMessage(), exception);
                    }
                });

                messageCount++;
                // Log stats every 10000 messages or 5 seconds
                long now = System.currentTimeMillis();
                if (messageCount % 10000 == 0 || now - lastLog > 5000) {
                    logger.info("Thread {} produced {} messages. Last message: {}", threadId, messageCount, value);
                    lastLog = now;
                }
            }
        } catch (Exception e) {
            logger.error("Failed to produce messages: {}", e.getMessage(), e);
        }
    }

    private static Map<String, Object> generateTransaction() {
        Map<String, Object> tx = new HashMap<>();
        tx.put("transaction_id", UUID.randomUUID().toString());
        tx.put("user_id", "user_" + ThreadLocalRandom.current().nextInt(1, 1001));
        tx.put("amount", ThreadLocalRandom.current().nextDouble(10.0, 1000.0));
        tx.put("transaction_time", System.currentTimeMillis() / 1000);
        tx.put("merchant_id", randomChoice("merchant_a", "merchant_b", "merchant_c"));
        tx.put("transaction_type", randomChoice("purchase", "refund", "transfer"));
        tx.put("location", "location_" + ThreadLocalRandom.current().nextInt(1, 6));
        tx.put("payment_method", randomChoice("credit_card", "debit_card", "paypal", "bank_transfer"));
        tx.put("is_international", ThreadLocalRandom.current().nextBoolean());
        tx.put("currency", randomChoice("USD", "EUR", "GBP", "JPY"));
        return tx;
    }

    private static String randomChoice(String... options) {
        return options[ThreadLocalRandom.current().nextInt(options.length)];
    }
}
