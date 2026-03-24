import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  registerAppResource,
  registerAppTool,
  RESOURCE_MIME_TYPE
} from "@modelcontextprotocol/ext-apps/server";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

type Todo = {
  id: string;
  title: string;
  completed: boolean;
};

const __dirname = dirname(fileURLToPath(import.meta.url));
const widgetPath = join(__dirname, "..", "public", "todo-widget.html");
const widgetHtml = readFileSync(widgetPath, "utf8");

const TEMPLATE_URI = "ui://widget/todo-v1.html";
const port = Number(process.env.PORT ?? 8787);
const mcpPath = "/mcp";

let todos: Todo[] = [];
let nextId = 1;

function buildTodoResult(message?: string) {
  return {
    content: message ? [{ type: "text" as const, text: message }] : [],
    structuredContent: { tasks: todos },
    _meta: {
      todoCount: todos.length,
      completedCount: todos.filter((todo) => todo.completed).length
    }
  };
}

function createTodoServer() {
  const server = new McpServer({
    name: "chatgpt-app-starter",
    version: "0.1.0"
  });

  registerAppResource(server, "todo-widget", TEMPLATE_URI, {}, async () => ({
    contents: [
      {
        uri: TEMPLATE_URI,
        mimeType: RESOURCE_MIME_TYPE,
        text: widgetHtml,
        _meta: {
          ui: {
            prefersBorder: true,
            csp: {
              connectDomains: [],
              resourceDomains: []
            }
          },
          "openai/widgetDescription":
            "Shows the todo list and lets the user add or complete items."
        }
      }
    ]
  }));

  registerAppTool(
    server,
    "list_todos",
    {
      title: "List todos",
      description:
        "Use this when the user wants the current todo list without changing anything.",
      inputSchema: { includeCompleted: z.boolean().default(true) },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        openWorldHint: false,
        idempotentHint: true
      },
      _meta: {
        ui: { resourceUri: TEMPLATE_URI },
        "openai/outputTemplate": TEMPLATE_URI,
        "openai/toolInvocation/invoking": "Loading todos",
        "openai/toolInvocation/invoked": "Todos ready"
      }
    },
    async ({ includeCompleted }) => {
      const visibleTodos = includeCompleted
        ? todos
        : todos.filter((todo) => !todo.completed);

      return {
        content: [{ type: "text" as const, text: "Showing the current todo list." }],
        structuredContent: { tasks: visibleTodos },
        _meta: {
          todoCount: todos.length,
          completedCount: todos.filter((todo) => todo.completed).length
        }
      };
    }
  );

  registerAppTool(
    server,
    "add_todo",
    {
      title: "Add todo",
      description: "Use this when the user wants to create a new todo item.",
      inputSchema: { title: z.string().trim().min(1).max(200) },
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        openWorldHint: false,
        idempotentHint: false
      },
      _meta: {
        ui: { resourceUri: TEMPLATE_URI },
        "openai/outputTemplate": TEMPLATE_URI,
        "openai/toolInvocation/invoking": "Adding todo",
        "openai/toolInvocation/invoked": "Todo added"
      }
    },
    async ({ title }) => {
      const todo: Todo = {
        id: `todo-${nextId++}`,
        title,
        completed: false
      };
      todos = [...todos, todo];
      return buildTodoResult(`Added "${todo.title}".`);
    }
  );

  registerAppTool(
    server,
    "complete_todo",
    {
      title: "Complete todo",
      description:
        "Use this when the user wants to mark an existing todo item as done.",
      inputSchema: { id: z.string().trim().min(1) },
      annotations: {
        readOnlyHint: false,
        destructiveHint: false,
        openWorldHint: false,
        idempotentHint: true
      },
      _meta: {
        ui: { resourceUri: TEMPLATE_URI },
        "openai/outputTemplate": TEMPLATE_URI,
        "openai/toolInvocation/invoking": "Completing todo",
        "openai/toolInvocation/invoked": "Todo completed"
      }
    },
    async ({ id }) => {
      const existing = todos.find((todo) => todo.id === id);
      if (!existing) {
        return buildTodoResult(`Todo ${id} was not found.`);
      }

      todos = todos.map((todo) =>
        todo.id === id ? { ...todo, completed: true } : todo
      );

      return buildTodoResult(`Completed "${existing.title}".`);
    }
  );

  return server;
}

const httpServer = createServer(async (req, res) => {
  if (!req.url) {
    res.writeHead(400).end("Missing URL");
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host ?? "localhost"}`);

  if (req.method === "OPTIONS" && url.pathname === mcpPath) {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "content-type, mcp-session-id",
      "Access-Control-Expose-Headers": "Mcp-Session-Id"
    });
    res.end();
    return;
  }

  if (req.method === "GET" && url.pathname === "/") {
    res.writeHead(200, { "content-type": "text/plain; charset=utf-8" });
    res.end(`ChatGPT app starter listening on http://localhost:${port}${mcpPath}`);
    return;
  }

  if (
    url.pathname === mcpPath &&
    req.method &&
    ["GET", "POST", "DELETE"].includes(req.method)
  ) {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Expose-Headers", "Mcp-Session-Id");

    const server = createTodoServer();
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true
    });

    res.on("close", () => {
      transport.close();
      server.close();
    });

    try {
      await server.connect(transport);
      await transport.handleRequest(req, res);
    } catch (error) {
      console.error("Error handling MCP request", error);
      if (!res.headersSent) {
        res.writeHead(500).end("Internal server error");
      }
    }
    return;
  }

  res.writeHead(404).end("Not Found");
});

httpServer.listen(port, () => {
  console.log(`ChatGPT app starter listening on http://localhost:${port}${mcpPath}`);
});
