// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Java's built-in HttpClient (Java 11+). To keep this program runnable ANYWHERE (offline, in a sandbox,
 * with no flaky third-party API) we start a tiny HTTP server on this machine's loopback address, on a free port,
 * and call that. The client code is exactly what you would use against a real API:
 * only the URL would change (e.g. https://api.example.com/users/1).
 */
public class _6_HttpClient {

    static HttpServer startServer() throws IOException {
        // port 0 = "any free port"; bound to loopback only, so nothing outside this machine can connect
        HttpServer server = HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), 0), 0);

        server.createContext("/users/1", exchange -> {
            String body = "{\"id\": 1, \"name\": \"Ada Lovelace\", \"city\": \"London\"}";
            respond(exchange, 200, "application/json", body);
        });
        server.createContext("/echo", exchange -> {
            String received = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
            respond(exchange, 201, "text/plain", "server received " + exchange.getRequestMethod() + ": " + received);
        });
        server.createContext("/slow", exchange -> {
            try {
                Thread.sleep(1500);                                // slower than the client's patience
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            try {
                respond(exchange, 200, "text/plain", "too late");
            } catch (IOException ignored) {
                // the client already gave up and closed the connection
            }
        });
        server.start();
        return server;
    }

    static void respond(com.sun.net.httpserver.HttpExchange exchange, int status, String type, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", type);
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }

    // A deliberately tiny "parser" for one flat string field. For real JSON use Jackson (see 07 and 12).
    static String jsonField(String json, String field) {
        Matcher m = Pattern.compile("\"" + field + "\"\\s*:\\s*\"([^\"]*)\"").matcher(json);
        return m.find() ? m.group(1) : null;
    }

    public static void main(String[] args) throws Exception {

        HttpServer server = startServer();
        String base = "http://" + server.getAddress().getHostString() + ":" + server.getAddress().getPort();

        try {
            // ============================================
            // SECTION 1: THE CLIENT - BUILD ONCE, REUSE
            // HttpClient is immutable, thread-safe and holds a connection pool: create ONE and share it.
            // Always set a connect timeout.
            // ============================================

            HttpClient client = HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(2))
                    .build();

            // ============================================
            // SECTION 2: A GET REQUEST
            // Request = what to send (immutable, built with a builder).
            // Response = status code + headers + a BODY of the type chosen by the BodyHandler.
            // ============================================

            HttpRequest get = HttpRequest.newBuilder(URI.create(base + "/users/1"))
                    .header("Accept", "application/json")
                    .timeout(Duration.ofSeconds(2))                // per-request limit
                    .GET()
                    .build();

            HttpResponse<String> response = client.send(get, HttpResponse.BodyHandlers.ofString());
            System.out.println("status:       " + response.statusCode());
            System.out.println("content-type: " + response.headers().firstValue("Content-Type").orElse("none"));
            System.out.println("body:         " + response.body());
            System.out.println("parsed name:  " + jsonField(response.body(), "name") + ", city: " + jsonField(response.body(), "city"));


            // ============================================
            // SECTION 3: A POST REQUEST WITH A BODY
            // ============================================

            HttpRequest post = HttpRequest.newBuilder(URI.create(base + "/echo"))
                    .header("Content-Type", "text/plain")
                    .timeout(Duration.ofSeconds(2))
                    .POST(HttpRequest.BodyPublishers.ofString("hello server"))
                    .build();
            HttpResponse<String> postResponse = client.send(post, HttpResponse.BodyHandlers.ofString());
            System.out.println("POST status " + postResponse.statusCode() + ": " + postResponse.body());


            // ============================================
            // SECTION 4: STATUS CODES ARE NOT EXCEPTIONS
            // A 404 or 500 is a NORMAL response: send() does not throw. You must check the code.
            // ============================================

            HttpResponse<String> notFound = client.send(
                    HttpRequest.newBuilder(URI.create(base + "/does-not-exist")).timeout(Duration.ofSeconds(2)).build(),
                    HttpResponse.BodyHandlers.ofString());
            System.out.println("missing path -> status " + notFound.statusCode() + "  (no exception was thrown)");
            if (notFound.statusCode() / 100 != 2) {
                System.out.println("our code must decide what a non-2xx response means");
            }


            // ============================================
            // SECTION 5: TIMEOUTS - THE REQUEST THAT NEVER COMES BACK
            // Without a timeout, a slow server can block your thread for a very long time.
            // ============================================

            HttpRequest slow = HttpRequest.newBuilder(URI.create(base + "/slow")).timeout(Duration.ofMillis(300)).build();
            try {
                client.send(slow, HttpResponse.BodyHandlers.ofString());
            } catch (HttpTimeoutException e) {
                System.out.println("HttpTimeoutException: gave up after 300 ms");
            }


            // ============================================
            // SECTION 6: ASYNC - sendAsync RETURNS A CompletableFuture (see 05 and 08)
            // Fire three requests at once, then combine.
            // ============================================

            List<CompletableFuture<String>> futures = List.of(
                    client.sendAsync(get, HttpResponse.BodyHandlers.ofString()).thenApply(r -> "A:" + r.statusCode()),
                    client.sendAsync(get, HttpResponse.BodyHandlers.ofString()).thenApply(r -> "B:" + r.statusCode()),
                    client.sendAsync(post, HttpResponse.BodyHandlers.ofString()).thenApply(r -> "C:" + r.statusCode()));
            CompletableFuture.allOf(futures.toArray(new CompletableFuture<?>[0])).get();
            System.out.println("async results: " + futures.stream().map(CompletableFuture::join).toList());

            // ============================================
            // SECTION 7: RULES TO REMEMBER
            // 1) One shared HttpClient; set connectTimeout and a per-request timeout.
            // 2) Check statusCode(): HTTP errors do not throw.
            // 3) Network calls throw IOException/InterruptedException: handle both.
            // 4) Never put secrets (API keys) in source: read them from environment variables.
            // 5) Calling a real public API is the same code with a different URL. We use a local
            //    server here so the program works offline and is repeatable.
            // ============================================
        } finally {
            server.stop(0);
        }
    }
}
