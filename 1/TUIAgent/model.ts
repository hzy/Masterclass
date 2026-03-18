import { createOpenAI } from "@ai-sdk/openai";

const openai = createOpenAI({
  baseURL: "http://localhost:8000/v1",
  /* cspell:disable-next-line */
  apiKey: "sk-xxx",

  // uncomment this to see the requests and responses in the console
  // fetch: async (input: string | URL | Request, init?: BunFetchRequestInit) => {
  //   const res = await globalThis.fetch(input, init);
  //   console.log(init, res);
  //   return res;
  // },
});

export { openai };
