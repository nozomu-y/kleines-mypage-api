var spec = {
  swagger: "2.0",
  info: {
    version: "1.0.0",
    title: "Kleines Mypage API",
    license: {
      name: "MIT License",
      url: "https://github.com/nozomu-y/kleines-mypage-api/blob/main/LICENSE",
    },
  },
  host: "chorkleines.com/member/mypage/api",
  basePath: "/v1",
  tags: [
    {
      name: "auth",
    },
    {
      name: "profile",
    },
  ],
  schemes: ["https"],
  paths: {
    "/auth": {
      post: {
        tags: ["auth"],
        description: "",
        consumes: ["application/json"],
        produces: ["application/json"],
        parameters: [
          {
            in: "body",
            name: "body",
            required: true,
            schema: {
              type: "object",
              properties: {
                email: { type: "string", format: "email" },
                password: { type: "string", format: "password" },
              },
            },
          },
        ],
        responses: {
          200: {
            description: "",
            schema: {
              type: "object",
              properties: {
                user_id: {
                  type: "integer",
                },
                token: { type: "string" },
              },
            },
          },
        },
      },
    },
    "/profile/{user_id}": {
      get: {
        tags: ["profile"],
        description: "",
        consumes: ["application/json"],
        produces: ["application/json"],
        parameters: [
          {
            in: "header",
            name: "Authorization",
            type: "string",
            required: "true",
          },
          {
            in: "path",
            name: "user_id",
            required: true,
            shema: { type: "integer" },
          },
        ],
        responses: {
          200: {
            schema: {
              type: "object",
              properties: {
                user_id: { type: "integer" },
              },
            },
          },
        },
      },
    },
  },
  externalDocs: {
    description: "GitHub",
    url: "https://github.com/nozomu-y/kleines-mypage-api",
  },
};
