// Fetch ngrok public URL from local API
const http = require("http");

http
  .get("http://127.0.0.1:4040/api/tunnels", (res) => {
    let data = "";
    res.on("data", (chunk) => (data += chunk));
    res.on("end", () => {
      try {
        const url = JSON.parse(data).tunnels?.[0]?.public_url;
        if (url) {
          process.stdout.write(url);
          process.exit(0);
        }
      } catch (_) {}
      process.exit(1);
    });
  })
  .on("error", () => process.exit(1));
