/** Find next available port starting from `start`. Prints port to stdout. */
const net = require("net");

function findPort(start = 3001, maxAttempts = 100) {
  return new Promise((resolve, reject) => {
    function tryPort(port) {
      if (port >= start + maxAttempts) {
        return reject(new Error(`No available port in range ${start}–${start + maxAttempts}`));
      }
      const server = net.createServer();
      server.on("error", () => tryPort(port + 1));
      server.listen(port, "0.0.0.0", () => {
        server.close(() => resolve(port));
      });
    }
    tryPort(start);
  });
}

const start = parseInt(process.argv[2], 10) || 3001;
findPort(start).then((port) => {
  if (port !== start) {
    console.warn(`[Meitai Demo] Port ${start} is busy, using port ${port} instead.`);
  }
  console.log(port);
  process.exit(0);
}).catch((e) => {
  console.error(e.message);
  process.exit(1);
});
