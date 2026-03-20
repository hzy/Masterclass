import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as z from "zod/v4";

const FIXED_WEATHER = {
  condition: "sunny" as const,
  temperatureC: 24,
  temperatureF: 75.2,
  humidity: 45,
  windKph: 12,
};

const server = new McpServer(
  {
    name: "weather-mcp",
    version: "1.0.0",
    title: "Weather MCP",
  },
  {
    instructions:
      "Use get_weather to retrieve weather for a city. Provide city and optional country, and use unit to control celsius or fahrenheit output.",
  },
);

server.registerTool(
  "get_weather",
  {
    description: "Get weather data for a city.",
    inputSchema: {
      city: z.string().min(1).describe("City name, e.g. Shanghai"),
      country: z.string().optional().describe("Optional country or region"),
      unit: z
        .enum(["celsius", "fahrenheit"])
        .default("celsius")
        .describe("Temperature display unit"),
    },
    outputSchema: {
      city: z.string(),
      country: z.string().optional(),
      condition: z.enum(["sunny", "cloudy", "rainy", "windy", "snowy"]),
      temperature: z.number(),
      unit: z.enum(["celsius", "fahrenheit"]),
      humidity: z.number().int().min(0).max(100),
      windKph: z.number().int().nonnegative(),
      note: z.string(),
    },
  },
  async ({ city, country, unit }) => {
    const temperature =
      unit === "fahrenheit"
        ? FIXED_WEATHER.temperatureF
        : FIXED_WEATHER.temperatureC;

    const structuredContent = {
      city,
      country,
      condition: FIXED_WEATHER.condition,
      temperature,
      unit,
      humidity: FIXED_WEATHER.humidity,
      windKph: FIXED_WEATHER.windKph,
      note: "Fixed weather snapshot.",
    };

    const countrySuffix = country ? `, ${country}` : "";

    return {
      content: [
        {
          type: "text",
          text: `${city}${countrySuffix}: ${temperature} ${unit === "celsius" ? "C" : "F"}, ${FIXED_WEATHER.condition}, humidity ${FIXED_WEATHER.humidity}%, wind ${FIXED_WEATHER.windKph} kph.`,
        },
      ],
      structuredContent,
    };
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);

console.error("weather-mcp server started on stdio");
