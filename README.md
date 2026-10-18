# Ali Restaurant Chatbot - Docker Assignment

A small **rule-based** Python chatbot, with a webpage, SQLite food information, English/Arabic replies and temporary memory of the last dish. This is the original single-file version, not the TF-IDF or medical project. No pip packages are needed.

## Open in VS Code

Use **File > Open Folder** and choose this folder, then **Terminal > New Terminal**.

## Run without Docker

```powershell
python simple-ali-chatbot.py
```

Open http://127.0.0.1:8001/. Keep the terminal running. Ctrl+C stops it.

## Build and run with Docker

Start **Docker Desktop** first, using Linux containers. Run these commands inside this folder:

```powershell
docker build -t ali-chatbot:1.0 .
docker run -d --name ali-chatbot -p 127.0.0.1:8001:8001 -v ali-data:/data ali-chatbot:1.0
```

Open http://127.0.0.1:8001/. Stop any normal Python version using port 8001 first. The first build needs internet to download the Python base image; later builds reuse cached layers. Docker packages the program; it does not improve chatbot intelligence.

```powershell
docker ps
docker logs ali-chatbot
docker stop ali-chatbot
docker start ali-chatbot
```

The same container name cannot be used to create another container while it exists. Use `docker start ali-chatbot` to start the existing one. After rebuilding code, remove the stopped old container with `docker rm ali-chatbot`, then run the new image again using the original `docker run` command. The named volume `ali-data` retains the restaurant database when the container is replaced. Conversation memory remains temporary in the browser.

## Packaging

The Docker **image** packages the application and Python runtime; a **container** is a running instance of that image. A ZIP packages the source files, but does not contain the Python runtime or the built image.

To export an actual built Docker image as a file for another computer:

```powershell
docker save -o ali-chatbot-image.tar ali-chatbot:1.0
```

On a computer with Docker, import it with:

```powershell
docker load -i ali-chatbot-image.tar
```

Run it with the same `docker run` command. The image archive does not contain the runtime database in the named volume. Do not commit the large TAR archive or generated SQLite file to GitHub.

## What each Dockerfile line does

| Instruction | Meaning |
|---|---|
| `FROM python:3.12-slim` | Starts with a small Python Linux image. |
| `WORKDIR /app` | Sets the application folder inside the image. |
| `ENV ...` | Enables immediate logs, container networking and a separate database path. |
| `COPY ...` | Copies the single Python program into the image. |
| `RUN ...` | Creates a writable data folder owned by user 10001. |
| `USER 10001:10001` | Runs the program without administrator/root privileges. |
| `EXPOSE 8001` | Documents the container port; `docker run -p` actually publishes it. |
| `CMD ...` | Starts the chatbot when the container runs. |

Inside the container the program binds to `0.0.0.0` so Docker can reach it. The host port is published only at `127.0.0.1`, keeping this demo local. The Python code accepts `HOST` and `DATABASE_PATH` from environment variables; local defaults still work. Database connections are explicitly closed after use.

## Publish to GitHub using VS Code

1. Open **this folder only**, not the larger folder containing other projects.
2. Open **Source Control** (`Ctrl+Shift+G`) and choose **Initialize Repository** if needed.
3. Review the files. The generated database, environments and archives should be ignored.
4. Stage the files with **+**, enter `Package Ali chatbot with Docker`, and choose **Commit**. Git may request your author name/email if not configured.
5. Choose **Publish Branch / Publish to GitHub** (also available from the Command Palette).
6. Sign in to GitHub yourself if requested. Choose the repository name and public/private visibility. Use a public repository only if your teacher requires public access.
7. Open the repository on GitHub and verify the Python file, Dockerfile, ignore files and README appear.

For an existing repository, use **Git: Add Remote** from the Command Palette, add its URL as `origin`, then **Push**. Check that its history is compatible first; do not force-push over existing work.

## Simple demonstration

Ask `hello`, `menu`, `burger`, `how much is it?`, then `ingredients`. Switch the language selector for Arabic. Refresh or New chat clears the selected dish. Restaurant seed data is illustrative; opening hours are not supplied.

## What to say in class

"I packaged my existing Python chatbot with Docker. The Dockerfile defines its runtime and startup command. I use a named volume to keep SQLite data, and publish the project source to GitHub through VS Code."

References: [Dockerfile instructions](https://docs.docker.com/reference/dockerfile/), [Docker volumes](https://docs.docker.com/engine/storage/volumes/), [VS Code and GitHub](https://code.visualstudio.com/docs/sourcecontrol/github).
