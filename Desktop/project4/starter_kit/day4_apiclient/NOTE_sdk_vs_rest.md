# SDK or REST: when to use which

**Use the provider's SDK when:**
- Authentication is complex (for example AWS request signing with boto3). The SDK gets it right and keeps it updated.
- The SDK already handles retries, pagination and typed responses, so I write less code and fewer bugs.
- The integration will live for a long time. SDK updates follow API changes.

**Call the REST API myself when:**
- I need only one or two endpoints, and a large SDK is too heavy a dependency.
- No SDK exists for my language, or it is missing a new endpoint.
- I need full control over requests, timeouts, retries and logging, or one client for many providers.

**My rule:** start with the SDK if it is well maintained and covers my endpoints.
Write my own client (like this `apiclient`) when the SDK does not fit, and then handle
timeouts, retries with backoff, pagination and validation myself.
