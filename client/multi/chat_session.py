import logging

from anthropic import Anthropic

from multi.server import Server


class ChatSession:
    """Orchestrates the interaction between user, LLM, and tools."""

    def __init__(self, servers: list[Server], anthropic: Anthropic) -> None:
        self.servers: list[Server] = servers
        self.anthropic: Anthropic = anthropic

    async def cleanup_servers(self) -> None:
        for server in reversed(self.servers):
            try:
                await server.cleanup()
            except Exception as e:
                logging.warning(f"Warning during final cleanup: {e}")

    async def start(self) -> None:
        """Main chat session handler."""
        try:
            for server in self.servers:
                try:
                    await server.initialize()
                except Exception as e:
                    logging.error(f"Failed to initialize server: {e}")
                    return

            all_tools = []
            for server in self.servers:
                tools = await server.list_tools()
                all_tools.extend(tools)

            available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            } for tool in all_tools]

            while True:
                try:
                    user_input = input("You: ").strip().lower()
                    if user_input in ["quit", "exit"]:
                        logging.info("\nExiting...")
                        break

                    messages = [{"role": "user", "content": user_input}]
                    response = self.anthropic.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1000,
                        messages=messages,
                        tools=available_tools
                    )

                    logging.info("\nAssistant: %s", response)

                    final_text = []
                    for content in response.content:
                        if content.type == 'text':
                            final_text.append(content.text)
                        elif content.type == 'tool_use':
                            tool_name = content.name
                            tool_args = content.input
                            logging.info(f"[Calling tool {tool_name} with args {tool_args}]")

                            for server in self.servers:
                                tools = await server.list_tools()
                                if any(tool.name == tool_name for tool in tools):
                                    try:
                                        result = await server.execute_tool(tool_name, tool_args)

                                        if isinstance(result, dict) and "progress" in result:
                                            progress = result["progress"]
                                            total = result["total"]
                                            percentage = (progress / total) * 100
                                            logging.info(
                                                f"Progress: {progress}/{total} "
                                                f"({percentage:.1f}%)"
                                            )

                                        # Continue conversation with tool results
                                        if hasattr(content, 'text') and content.text:
                                            messages.append({
                                                "role": "assistant",
                                                "content": content.text
                                            })
                                        messages.append({
                                            "role": "user",
                                            "content": result.content
                                        })
                                        # final_text.append(f"Tool execution result: {result}")
                                    except Exception as e:
                                        error_msg = f"Error executing tool: {str(e)}"
                                        logging.error(error_msg)
                                        final_text.append(error_msg)

                            # Execute tool call
                            # result = await self.session.call_tool(tool_name, tool_args)

                            # Get next response from Claude
                            response = self.anthropic.messages.create(
                                model="claude-3-5-sonnet-20241022",
                                max_tokens=1000,
                                messages=messages,
                            )

                            final_text.append(response.content[0].text)
                    print("\n" + "\n".join(final_text))

                except KeyboardInterrupt:
                    logging.info("\nExiting...")
                    break

        finally:
            await self.cleanup_servers()
