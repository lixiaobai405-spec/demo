/** Find the next available port starting from `start`. Prints the port to stdout. */
const net = require("net");

function canListen(port, host) {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();

    server.once("error", (error) => {
      reject(error);
    });

    server.listen({ port, host, exclusive: true }, () => {
      server.close((closeError) => {
        if (closeError) {
          reject(closeError);
          return;
        }
        resolve();
      });
    });
  });
}

async function isPortAvailable(port) {
  try {
    await canListen(port, "::");
    return true;
  } catch (error) {
    if (error.code === "EAFNOSUPPORT") {
      try {
        await canListen(port, "0.0.0.0");
        return true;
      } catch {
        return false;
      }
    }

    return false;
  }
}

async function findPort(start = 3001, maxAttempts = 100) {
  for (let port = start; port < start + maxAttempts; port += 1) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }

  throw new Error(`No available port in range ${start}-${start + maxAttempts - 1}`);
}

const start = parseInt(process.argv[2], 10) || 3001;

findPort(start)
  .then((port) => {
    if (port !== start) {
      console.warn(`[Meitai Demo] Port ${start} is busy, using port ${port} instead.`);
    }

    console.log(port);
    process.exit(0);
  })
  .catch((error) => {
    console.error(error.message);
    process.exit(1);
  });
