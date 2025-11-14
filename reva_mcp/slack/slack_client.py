from slack_connector import slack
from slack_connector.client import create_slack_client
from agent_handler_sdk.auth import AuthContext
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
import time
from slack_connector.models.message_types import (
    Message, MessageConnection, MessageSendResult, MessageUpdateResult, MessageDeleteResult,
    MessageSearchResult, SendMessageInput, UpdateMessageInput, DeleteMessageInput,
    GetMessagesInput, GetConversationHistoryInput, SearchMessagesInput, ReactionResult,
    PageInfo, GetConversationRepliesInput, GetConversationRepliesResult, AddReactionInput, RemoveReactionInput,
    GetUnreadDMsInput, GetUnreadDMsResult, UnreadDMConversation,
    GetUnreadChannelMessagesInput, GetUnreadChannelMessagesResult, UnreadChannelConversation,
    ScheduledMessage, ListScheduledMessagesInput, ListScheduledMessagesResult,
    GetUnreadMessagesFromChannelInput, GetUnreadMessagesFromChannelResult,
    GetUnreadMessagesFromUserInput, GetUnreadMessagesFromUserResult
)
from slack_connector.models.channel_types import Channel
from slack_connector.utils.channel_helper import create_channel_helper

def create_client(auth_context: AuthContext):
    """Create Slack client for message operations."""
    return create_slack_client(auth_context)


def _make_request_with_retry(client, method_name, max_retries=3, **kwargs):
    """
    Make a Slack API request with automatic retry on rate limit errors.

    Args:
        client: SlackClient instance
        method_name: Name of the client method to call (e.g., 'get_conversation_history')
        max_retries: Maximum number of retry attempts
        **kwargs: Arguments to pass to the method

    Returns:
        API response dictionary
    """
    import time

    for attempt in range(max_retries):
        try:
            method = getattr(client, method_name)
            response = method(**kwargs)

            # Check if response indicates rate limiting
            if isinstance(response, dict) and not response.get("ok"):
                error = response.get("error", "")
                if error == "rate_limited":
                    # Slack rate limited - use exponential backoff
                    wait_time = (2 ** attempt) * 1  # 1s, 2s, 4s
                    time.sleep(wait_time)
                    continue

            return response

        except Exception as e:
            # Check if it's an HTTP 429 error
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                if e.response.status_code == 429:
                    # Get retry-after header or use exponential backoff
                    retry_after = int(e.response.headers.get('Retry-After', 2 ** attempt))
                    time.sleep(retry_after)
                    continue

            # For other exceptions, propagate
            if attempt == max_retries - 1:
                raise

    # If all retries exhausted, return the last response
    return response


def _paginate_conversations(client, **params):
    """Helper function to paginate through all conversations."""
    all_conversations = []
    cursor = None
    max_iterations = 50  # Safety limit to prevent infinite loops
    iteration_count = 0
    
    while iteration_count < max_iterations:
        iteration_count += 1
        
        # Add cursor to params if we have one
        current_params = params.copy()
        if cursor:
            current_params['cursor'] = cursor
        
        response = client.list_conversations(**current_params)
        
        if not response.get("ok"):
            break
            
        conversations = response.get("channels", [])
        all_conversations.extend(conversations)
        
        # Check for more data
        response_metadata = response.get("response_metadata", {})
        next_cursor = response_metadata.get("next_cursor")
        
        if not next_cursor:
            break
        
        cursor = next_cursor
    
    return all_conversations


def _paginate_conversation_history(client, channel, **params):
    """Helper function to paginate through conversation history."""
    all_messages = []
    cursor = None
    max_iterations = 50  # Safety limit to prevent infinite loops
    iteration_count = 0
    
    while iteration_count < max_iterations:
        iteration_count += 1
        
        # Add cursor to params if we have one
        current_params = params.copy()
        if cursor:
            current_params['cursor'] = cursor
        
        response = client.get_conversation_history(channel=channel, **current_params)
        
        if not response.get("ok"):
            break
            
        messages = response.get("messages", [])
        all_messages.extend(messages)
        
        # Check for more data using has_more
        has_more = response.get("has_more", False)
        if not has_more:
            break
        
        # Get cursor from response_metadata
        response_metadata = response.get("response_metadata", {})
        next_cursor = response_metadata.get("next_cursor")
        
        if not next_cursor:
            break
        
        cursor = next_cursor
    
    return all_messages


@slack.tool(name="post_message", desc="Send a message to a Slack channel using Channel ID (not channel name)")
def post_message(
    input: SendMessageInput,
    auth_context: Optional[AuthContext] = None
) -> MessageSendResult:
    """
    Send a message to a Slack channel or direct message.
    
    Args:
        input: Message data including channel, text, and optional formatting
        auth_context: Authentication context
        
    Returns:
        Message data including timestamp and channel info
    """
    client = create_slack_client(auth_context)
    
    # Build parameters dict, filtering out None values
    params = {
        "channel": input.channel,
        "text": input.text,
    }
    
    # Add optional parameters only if they are not None
    if input.blocks is not None:
        params["blocks"] = input.blocks
    if input.attachments is not None:
        params["attachments"] = input.attachments
    if input.thread_ts is not None:
        params["thread_ts"] = input.thread_ts
    if input.username is not None:
        params["username"] = input.username
    if input.icon_emoji is not None:
        params["icon_emoji"] = input.icon_emoji
    if input.icon_url is not None:
        params["icon_url"] = input.icon_url
    if input.as_user is not None:
        params["as_user"] = input.as_user
    if input.reply_broadcast is not None:
        params["reply_broadcast"] = input.reply_broadcast
    if input.unfurl_links is not None:
        params["unfurl_links"] = input.unfurl_links
    if input.unfurl_media is not None:
        params["unfurl_media"] = input.unfurl_media
    if input.link_names is not None:
        params["link_names"] = input.link_names
    if input.parse is not None:
        params["parse"] = input.parse
    if input.metadata is not None:
        params["metadata"] = input.metadata
        
    result = client.post_message(**params)
    
    if result.get("ok"):
        message_data = result.get("message", {})
        channel_data = message_data.get("channel")
        if channel_data:
            message_data["channel"] = Channel(**channel_data)
        
        # Create message with resolved usernames
        from slack_connector.utils.message_helpers import create_message_with_resolved_users
        from slack_connector.utils.user_resolver import create_user_resolver
        user_resolver = create_user_resolver(client)
        message = create_message_with_resolved_users(message_data, user_resolver)
        
        # Extract channel ID from channel data for the result
        channel_id = result.get("channel")
        if isinstance(channel_id, dict):
            channel_id = channel_id.get("id", channel_id.get("name", str(channel_id)))
        
        return MessageSendResult(
            success=True,
            message="Message sent successfully",
            ts=result.get("ts"),
            channel=channel_id,
            permalink=f"https://slack.com/archives/{channel_id}/p{result.get('ts', '').replace('.', '')}",
            sent_message=message
        )
    else:
        return MessageSendResult(
            success=False,
            message=result.get("error", "Failed to send message"),
            ts=None,
            channel=None,
            permalink=None,
            sent_message=None
        )


@slack.tool(name="update_message", desc="Update an existing message in Slack")
def update_message(
    input: UpdateMessageInput,
    auth_context: Optional[AuthContext] = None
) -> MessageUpdateResult:
    """
    Update an existing message in Slack.
    
    Args:
        input: Update data including channel, timestamp, and new content
        auth_context: Authentication context
        
    Returns:
        Updated message data
    """
    client = create_slack_client(auth_context)
    result = client.update_message(
        channel=input.channel,
        ts=input.ts,
        text=input.text,
        blocks=input.blocks,
        attachments=input.attachments
    )
    
    if result.get("ok"):
        return MessageUpdateResult(
            success=True,
            message="message_updated",
            ts=input.ts
        )
    else:
        return MessageUpdateResult(
            success=False,
            message=result.get("error", "Failed to update message"),
            ts=input.ts
        )


@slack.tool(name="delete_message", desc="Delete a message from Slack")
def delete_message(
    input: DeleteMessageInput,
    auth_context: Optional[AuthContext] = None
) -> MessageDeleteResult:
    """
    Delete a message from Slack.
    
    Args:
        channel: Channel ID where the message exists
        ts: Timestamp of the message to delete
        auth_context: Authentication context
        
    Returns:
        Confirmation of deletion
    """
    client = create_slack_client(auth_context)
    result = client.delete_message(input.channel, input.ts)
    
    if result.get("ok"):
        return MessageDeleteResult(
            success=True,
            message="Message deleted successfully",
            ts=input.ts
        )
    else:
        return MessageDeleteResult(
            success=False,
            message=result.get("error", "Failed to delete message"),
            ts=input.ts
        )


@slack.tool(name="get_message_permalink", desc="Get a permanent link to a message")
def get_message_permalink(
    channel: str,
    message_ts: str,
    auth_context: Optional[AuthContext] = None
) -> Dict[str, Any]:
    """
    Get a permanent link to a message.
    
    Args:
        channel: Channel ID where the message exists
        message_ts: Timestamp of the message
        auth_context: Authentication context
        
    Returns:
        Permalink URL to the message
    """
    client = create_slack_client(auth_context)
    result = client.get_message_permalink(channel, message_ts)
    
    return {
        "permalink": result.get("permalink"),
        "channel": channel,
        "message_ts": message_ts,
        "success": True
    }


@slack.tool(name="get_conversation_history", desc="Get message history from a channel using Channel ID with enhanced timestamp filtering. For time windows: use Unix timestamps (oldest='1640995200.123456', latest='1640995300.123456') OR convenient parameters (days_ago=7, hours_ago=24, start_date='2023-12-01', end_date='2023-12-15'). Set inclusive=True to include boundary messages.")
def get_conversation_history(
    input: GetConversationHistoryInput,
    auth_context: Optional[AuthContext] = None
) -> MessageConnection:
    """
    Get message history from a channel with enhanced timestamp filtering.
    
    TIMESTAMP FILTERING OPTIONS:
    Method 1 - Unix timestamps (existing):
    - oldest='1640995200.123456', latest='1640995300.123456'
    - Messages with exact timestamps are excluded unless inclusive=True
    
    Method 2 - Convenience parameters (new):
    - days_ago=7 - Messages from past 7 days
    - hours_ago=24 - Messages from past 24 hours  
    - start_date='2023-12-01', end_date='2023-12-15' - Precise date ranges
    
    Note: Existing oldest/latest parameters take precedence over convenience parameters.
    
    Args:
        input: Parameters for history retrieval including channel and time range options.
        auth_context: Authentication context
    Returns:
        List of messages with metadata and pagination info.
        When presenting to users, always display username/user_name fields instead 
        of user_id fields for better user experience.
    """
    client = create_slack_client(auth_context)
    
    # Apply enhanced timestamp filtering
    latest = input.latest
    oldest = input.oldest
    
    # Only apply convenience timestamp params if no timestamps already provided
    if not latest and not oldest:
        from datetime import datetime, timedelta
        import time
        
        # Priority: start_date/end_date > days_ago/hours_ago
        if input.start_date or input.end_date:
            if input.start_date:
                # Convert YYYY-MM-DD to Unix timestamp (start of day)
                start_dt = datetime.strptime(input.start_date, "%Y-%m-%d")
                oldest = str(start_dt.timestamp())
            if input.end_date:
                # Convert YYYY-MM-DD to Unix timestamp (end of day)
                end_dt = datetime.strptime(input.end_date, "%Y-%m-%d")
                end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                latest = str(end_dt.timestamp())
        elif input.days_ago is not None or input.hours_ago is not None:
            if input.days_ago is not None:
                target_time = time.time() - (input.days_ago * 24 * 60 * 60)
                oldest = str(target_time)
            elif input.hours_ago is not None:
                target_time = time.time() - (input.hours_ago * 60 * 60)
                oldest = str(target_time)
    
    result = client.get_conversation_history(
        channel=input.channel,
        latest=latest,
        oldest=oldest,
        inclusive=input.inclusive,
        limit=input.limit,
        cursor=input.cursor
    )
    
    # Convert messages to Pydantic models with resolved usernames
    from slack_connector.utils.message_helpers import create_messages_with_resolved_users
    messages = create_messages_with_resolved_users(result.get("messages", []), client)
 
    # Return the response in Slack's native format
    return MessageConnection(
        ok=result.get("ok", True),
        messages=messages,
        has_more=result.get("has_more", False),
        pin_count=result.get("pin_count", 0),
        channel_actions_ts=result.get("channel_actions_ts"),
        channel_actions_count=result.get("channel_actions_count", 0),
        response_metadata=result.get("response_metadata")
    )


@slack.tool(name="schedule_message", desc="Schedule a message to be sent later")
def schedule_message(
    channel: str,
    text: str,
    post_at: int,
    thread_ts: Optional[str] = None,
    blocks: Optional[List[Dict[str, Any]]] = None,
    auth_context: Optional[AuthContext] = None
) -> Dict[str, Any]:
    """
    Schedule a message to be sent at a future time.
    
    Args:
        channel: Channel ID to send message to
        text: Message text content
        post_at: Unix timestamp when to send the message
        thread_ts: Timestamp of parent message to reply in thread
        blocks: Block Kit blocks for rich formatting
        auth_context: Authentication context
        
    Returns:
        Scheduled message information
    """
    client = create_slack_client(auth_context)
    
    data = {
        "channel": channel,
        "text": text,
        "post_at": post_at
    }
    
    if thread_ts:
        data["thread_ts"] = thread_ts
    if blocks:
        data["blocks"] = blocks
    
    result = client.schedule_message(**data)
    
    return {
        "scheduled_message_id": result.get("scheduled_message_id"),
        "channel": result.get("channel"),
        "post_at": result.get("post_at"),
        "message": result.get("message", {}),
        "success": True
    }


@slack.tool(name="delete_scheduled_message", desc="Delete a scheduled message")
def delete_scheduled_message(
    channel: str,
    scheduled_message_id: str,
    auth_context: Optional[AuthContext] = None
) -> Dict[str, Any]:
    """
    Delete a scheduled message before it's sent.
    
    Args:
        channel: Channel ID where the message was scheduled
        scheduled_message_id: ID of the scheduled message
        auth_context: Authentication context
        
    Returns:
        Confirmation of deletion
    """
    client = create_slack_client(auth_context)
    
    data = {
        "channel": channel,
        "scheduled_message_id": scheduled_message_id
    }
    
    result = client.delete_scheduled_message(**data)
    
    return {
        "success": True,
        "message": f"Scheduled message {scheduled_message_id} deleted successfully"
    }


@slack.tool(name="add_reaction", desc="Add an emoji reaction to a message") 
def add_reaction(
    channel: str,
    timestamp: str,
    name: str,
    auth_context: Optional[AuthContext] = None
) -> ReactionResult:
    """
    Add an emoji reaction to a message.
    
    Args:
        channel: Channel ID where the message exists
        timestamp: Timestamp of the message to react to
        name: Name of emoji to use as reaction (without colons)
        auth_context: Authentication context
        
    Returns:
        Confirmation of reaction addition
    """
    client = create_slack_client(auth_context)
    
    data = {
        "channel": channel,
        "timestamp": timestamp,
        "name": name
    }
    
    result = client.add_reaction(**data)
    
    if result.get("ok"):
        return ReactionResult(
            success=True,
            message=f":{name}: reaction added successfully"
        )
    else:
        return ReactionResult(
            success=False,
            message=result.get("error", "Failed to add reaction")
        )


@slack.tool(name="remove_reaction", desc="Remove an emoji reaction from a message")
def remove_reaction(
    channel: str,
    timestamp: str,
    name: str,
    auth_context: Optional[AuthContext] = None
) -> ReactionResult:
    """
    Remove an emoji reaction from a message.
    
    Args:
        channel: Channel ID where the message exists
        timestamp: Timestamp of the message
        name: Name of emoji reaction to remove (without colons)
        auth_context: Authentication context
        
    Returns:
        Confirmation of reaction removal
    """
    client = create_slack_client(auth_context)
    
    data = {
        "channel": channel,
        "timestamp": timestamp,
        "name": name
    }
    
    result = client.remove_reaction(**data)
    
    if result.get("ok"):
        return ReactionResult(
            success=True,
            message=f":{name}: reaction removed successfully"
        )
    else:
        return ReactionResult(
            success=False,
            message=result.get("error", "Failed to remove reaction")
        )


@slack.tool(name="get_conversation_replies", desc="Get all replies in a Slack thread. This tool MUST be called whenever you encounter a message with reply_count > 0 from get_conversation_history, search_messages, or any message-fetching tool to provide complete conversation context. When presenting results to users, always display username/display_name instead of user_id for better readability.")
def get_conversation_replies(
    input: GetConversationRepliesInput,
    auth_context: Optional[AuthContext] = None
) -> MessageConnection:
    """
    Get all replies in a thread.
    
    This tool should ALWAYS be called when you encounter a message with reply_count > 0
    to get the complete conversation context including all thread replies.
    
    Args:
        input: Parameters for getting thread replies including channel, parent message timestamp, and pagination options
        auth_context: Authentication context
        
    Returns:
        List of messages in the thread with pagination info.
        When presenting to users, always display username/user_name fields instead 
        of user_id fields for better user experience.
    """
    client = create_slack_client(auth_context)
    result = client.get_conversation_replies(
        channel=input.channel,
        ts=input.ts,
        cursor=input.cursor,
        inclusive=input.inclusive,
        latest=input.latest,
        limit=input.limit,
        oldest=input.oldest
    )
    
    # Convert messages to Pydantic models with resolved usernames
    from slack_connector.utils.message_helpers import create_messages_with_resolved_users
    messages = create_messages_with_resolved_users(result.get("messages", []), client)
    
    # Create pagination info
    response_metadata = result.get("response_metadata", {})
    page_info = PageInfo(
        hasNextPage=result.get("has_more", False),
        hasPreviousPage=False,
        startCursor=None,
        endCursor=response_metadata.get("next_cursor")
    )
    
    return GetConversationRepliesResult(**result)


@slack.tool(name="list_unread_direct_messages", desc="Get all unread direct messages and group DMs with their message content. When presenting results to users, always display username/display_name instead of user_id for better readability.")
def list_unread_direct_messages(
    input: GetUnreadDMsInput,
    auth_context: Optional[AuthContext] = None
) -> GetUnreadDMsResult:
    """
    List all unread direct messages and group DMs with their message content.

    This tool retrieves all direct message conversations that have unread messages,
    along with the actual message content. It automatically detects which conversations
    have unreads and fetches only the messages that haven't been read yet.

    Args:
        input: Parameters for getting unread DMs including conversation limit and whether to include group DMs
        auth_context: Authentication context

    Returns:
        List of DM conversations with unread messages and their content.
        When presenting to users, always display username/user_name fields instead
        of user_id fields for better user experience.
    """
    client = create_slack_client(auth_context)
    
    try:
        # Get conversations with unread counts
        conversation_types = "im"
        if input.include_group_dms:
            conversation_types += ",mpim"
            
        # Use optimized pagination with Slack's recommended batch size
        conversations = _paginate_conversations(
            client,
            types=conversation_types,
            limit=200,  # Slack's recommended max for optimal performance
            exclude_archived=True
        )
        
        if not conversations:
            return GetUnreadDMsResult(
                success=False,
                unread_conversations=[],
                total_unread_count=0,
                conversations_checked=0,
                message="Failed to fetch conversations or no conversations found"
            )
        
        unread_conversations = []
        total_unread_count = 0

        # Filter to conversations with unread messages
        conversations_with_unreads = [
            conv for conv in conversations 
            if conv.get("unread_count", 0) > 0 or conv.get("unread_count_display", 0) > 0
        ]
        
        # Create shared user resolver for efficiency
        from slack_connector.utils.user_resolver import create_user_resolver
        user_resolver = create_user_resolver(client)

        # Fetch message history for all conversations with unreads first
        # This allows us to batch user resolution across all conversations
        conversations_with_messages = []

        for conversation in conversations_with_unreads:
            try:
                unread_count = conversation.get("unread_count", 0)
                last_read = conversation.get("last_read")

                # Skip if no unread messages (safety check)
                if unread_count == 0:
                    continue

                # Determine timestamp
                oldest = last_read if last_read else str(time.time() - (24 * 60 * 60))  # fallback to 24h

                # Smart pagination: use pagination if many unreads, single call otherwise
                messages_data = []
                if unread_count > 190:  # Close to 200 limit
                    # Use pagination to get all messages
                    messages_data = _paginate_conversation_history(
                        client,
                        channel=conversation["id"],
                        oldest=oldest,
                        inclusive=False
                    )
                else:
                    # Single call sufficient with retry logic
                    messages_response = _make_request_with_retry(
                        client,
                        "get_conversation_history",
                        channel=conversation["id"],
                        oldest=oldest,
                        inclusive=False,
                        limit=min(unread_count + 10, 200)  # Dynamic limit based on unread count
                    )

                    if messages_response.get("ok"):
                        messages_data = messages_response.get("messages", [])

                if messages_data:
                    # Add permalinks
                    for message_data in messages_data:
                        if not message_data.get("permalink") and message_data.get("ts"):
                            message_ts = message_data["ts"].replace(".", "")
                            message_data["permalink"] = f"https://slack.com/archives/{conversation['id']}/p{message_ts}"

                    conversations_with_messages.append({
                        "conversation": conversation,
                        "messages": messages_data,
                        "unread_count": unread_count,
                        "last_read": last_read
                    })

            except Exception as e:
                # Skip this conversation if there's an error processing it
                continue

        # Batch user resolution - collect ALL user IDs from ALL conversations
        all_user_ids = set()
        for conv_data in conversations_with_messages:
            for msg_data in conv_data["messages"]:
                # Collect user IDs from messages
                if msg_data.get("user"):
                    all_user_ids.add(msg_data["user"])
                # Collect from reactions
                for reaction in msg_data.get("reactions", []):
                    all_user_ids.update(reaction.get("users", []))
                # Collect from reply users
                all_user_ids.update(msg_data.get("reply_users", []))
                # Collect parent user
                if msg_data.get("parent_user_id"):
                    all_user_ids.add(msg_data["parent_user_id"])

        # Batch resolve all user IDs upfront (single cache warm-up)
        if all_user_ids:
            user_resolver.resolve_user_ids_batch(list(all_user_ids))

        # Now process all conversations with pre-warmed cache
        from slack_connector.utils.message_helpers import create_message_with_resolved_users

        for conv_data in conversations_with_messages:
            try:
                conversation = conv_data["conversation"]
                messages_data = conv_data["messages"]
                unread_count = conv_data["unread_count"]
                last_read = conv_data["last_read"]

                unread_messages = []
                for message_data in messages_data:
                    # Create message with resolved usernames (uses pre-warmed cache)
                    message = create_message_with_resolved_users(message_data, user_resolver)
                    unread_messages.append(message)

                # Sort messages chronologically (oldest first)
                unread_messages.sort(key=lambda msg: float(msg.ts or "0"))
                
                # Determine conversation type and get user info
                is_group = conversation.get("is_mpim", False)
                user_id = conversation.get("user") if not is_group else None
                
                # Create unread conversation object with all available data from conversations.list
                unread_dm = UnreadDMConversation(
                    channel_id=conversation["id"],
                    channel_info=conversation,  # Use data from conversations.list directly
                    user_id=user_id,
                    unread_count=unread_count,
                    last_read=last_read,
                    unread_messages=unread_messages,
                    is_group=is_group
                )
                
                unread_conversations.append(unread_dm)
                total_unread_count += unread_count
                
            except Exception as e:
                # Skip this conversation if there's an error processing it
                continue
        
        return GetUnreadDMsResult(
            success=True,
            unread_conversations=unread_conversations,
            total_unread_count=total_unread_count,
            conversations_checked=len(conversations),
            message=f"Found {len(unread_conversations)} conversations with {total_unread_count} total unread messages"
        )
        
    except Exception as e:
        return GetUnreadDMsResult(
            success=False,
            unread_conversations=[],
            total_unread_count=0,
            conversations_checked=0,
            message=f"Error retrieving unread DMs: {str(e)}"
        )


@slack.tool(name="list_unread_channel_messages", desc="Get all unread messages from channels with their message content. Uses smart prioritization to check most recently active channels first. When presenting results to users, always display username/display_name instead of user_id for better readability.")
def list_unread_channel_messages(
    input: GetUnreadChannelMessagesInput,
    auth_context: Optional[AuthContext] = None
) -> GetUnreadChannelMessagesResult:
    """
    List all unread messages from channels with their message content.

    This tool retrieves messages from channels based on a time window (default: last 24 hours).
    Since Slack doesn't provide unread counts for channels, this tool checks recently active
    channels first and returns messages since the specified timestamp.

    Note: This fetches recent messages, not truly "unread" messages. For accurate unread
    detection in a specific channel, use get_unread_messages_from_channel instead.

    Args:
        input: Parameters for getting unread channel messages including channel types and timestamp
        auth_context: Authentication context

    Returns:
        List of channels with recent messages and their content.
        When presenting to users, always display username/user_name fields instead
        of user_id fields for better user experience.
    """
    client = create_slack_client(auth_context)
    
    try:
        # Calculate default since_ts if not provided (24 hours ago)
        if not input.since_ts:
            twenty_four_hours_ago = time.time() - (24 * 60 * 60)
            since_ts = str(twenty_four_hours_ago)
        else:
            since_ts = input.since_ts
        
        # Get channels with smart filtering
        channels = _paginate_conversations(
            client,
            types=input.channel_types,
            limit=200,  # Slack's recommended max for optimal performance
            exclude_archived=True
        )
        
        if not channels:
            return GetUnreadChannelMessagesResult(
                success=False,
                unread_conversations=[],
                total_unread_count=0,
                channels_checked=0,
                message="Failed to fetch channels or no channels found"
            )
        
        # Prioritize channels by recent activity
        def get_channel_priority(channel):
            # Prioritize based on latest message timestamp (if available)
            latest = float(channel.get("latest", {}).get("ts", "0"))
            created = float(channel.get("created", "0"))
            return max(latest, created)
        
        # Sort channels by priority (most recently active first)
        prioritized_channels = sorted(channels, key=get_channel_priority, reverse=True)

        # Limit channel processing for performance
        max_channels_to_check = min(len(prioritized_channels), 50)
        channels_to_process = prioritized_channels[:max_channels_to_check]
        
        unread_conversations = []
        total_unread_count = 0
        checked_count = 0
        
        # Create shared user resolver for efficiency
        from slack_connector.utils.user_resolver import create_user_resolver
        user_resolver = create_user_resolver(client)

        # Fetch messages from prioritized channels
        for channel in channels_to_process:
            try:
                checked_count += 1
                channel_id = channel["id"]

                # Fetch recent messages from channel with retry logic
                messages_response = _make_request_with_retry(
                    client,
                    "get_conversation_history",
                    channel=channel_id,
                    oldest=since_ts,
                    inclusive=False,
                    limit=200  # Slack's recommended batch size
                )
                
                if not messages_response.get("ok"):
                    continue
                    
                messages_data = messages_response.get("messages", [])
                
                # Skip if no new messages
                if not messages_data:
                    continue

                # Process messages with shared resolver
                unread_messages = []
                oldest_ts = None
                
                for message_data in messages_data:
                    # Add permalink for better UX
                    if not message_data.get("permalink") and message_data.get("ts"):
                        message_ts = message_data["ts"].replace(".", "")
                        message_data["permalink"] = f"https://slack.com/archives/{channel_id}/p{message_ts}"
                    
                    # Create message with resolved usernames using shared resolver
                    from slack_connector.utils.message_helpers import create_message_with_resolved_users
                    message = create_message_with_resolved_users(message_data, user_resolver)
                    unread_messages.append(message)
                    
                    # Track oldest message timestamp
                    if oldest_ts is None or message_data.get("ts", "") < oldest_ts:
                        oldest_ts = message_data.get("ts")
                
                # Sort messages chronologically (oldest first)
                unread_messages.sort(key=lambda msg: float(msg.ts or "0"))
                
                # Create unread channel conversation object
                unread_channel = UnreadChannelConversation(
                    channel_id=channel_id,
                    channel_info=channel,
                    unread_messages=unread_messages,
                    oldest_unread_ts=oldest_ts
                )
                
                unread_conversations.append(unread_channel)
                total_unread_count += len(unread_messages)

                # Early termination to avoid excessive processing
                if len(unread_conversations) >= 20:
                    break
                
            except Exception as e:
                # Skip this channel if there's an error processing it
                continue
        
        return GetUnreadChannelMessagesResult(
            success=True,
            unread_conversations=unread_conversations,
            total_unread_count=total_unread_count,
            channels_checked=checked_count,
            message=f"Found {len(unread_conversations)} channels with {total_unread_count} unread messages"
        )
        
    except Exception as e:
        return GetUnreadChannelMessagesResult(
            success=False,
            unread_conversations=[],
            total_unread_count=0,
            channels_checked=0,
            message=f"Error retrieving unread channel messages: {str(e)}"
        )


@slack.tool(name="list_scheduled_messages", desc="List scheduled messages that haven't been sent yet")
def list_scheduled_messages(
    input: ListScheduledMessagesInput,
    auth_context: Optional[AuthContext] = None
) -> ListScheduledMessagesResult:
    """
    List scheduled messages that haven't been sent yet.
    
    This tool retrieves all scheduled messages that are waiting to be sent,
    with optional filtering by channel or time range.
    
    Args:
        input: Parameters for listing scheduled messages including channel filter, time range, and pagination
        auth_context: Authentication context
        
    Returns:
        List of scheduled messages with their details including send times and content
    """
    client = create_slack_client(auth_context)
    
    try:
        result = client.list_scheduled_messages(
            channel=input.channel,
            cursor=input.cursor,
            latest=input.latest,
            oldest=input.oldest,
            limit=input.limit
        )
        
        if not result.get("ok"):
            return ListScheduledMessagesResult(
                success=False,
                scheduled_messages=[],
                response_metadata=None,
                message=f"Failed to list scheduled messages: {result.get('error', 'Unknown error')}"
            )
        
        # Convert scheduled messages to ScheduledMessage objects
        scheduled_messages = []
        for msg_data in result.get("scheduled_messages", []):
            scheduled_message = ScheduledMessage(
                id=msg_data.get("id", ""),
                channel_id=msg_data.get("channel_id", ""),
                post_at=msg_data.get("post_at", 0),
                date_created=msg_data.get("date_created", 0),
                text=msg_data.get("text"),
                user_id=msg_data.get("user_id")
            )
            scheduled_messages.append(scheduled_message)
        
        return ListScheduledMessagesResult(
            success=True,
            scheduled_messages=scheduled_messages,
            response_metadata=result.get("response_metadata"),
            message=f"Found {len(scheduled_messages)} scheduled messages"
        )
        
    except Exception as e:
        return ListScheduledMessagesResult(
            success=False,
            scheduled_messages=[],
            response_metadata=None,
            message=f"Error retrieving scheduled messages: {str(e)}"
        )


@slack.tool(name="get_unread_messages_from_channel", desc="Get all unread messages from a specific channel. Uses the channel's last_read timestamp to accurately identify unread messages. When presenting results to users, always display username/display_name instead of user_id for better readability.")
def get_unread_messages_from_channel(
    input: GetUnreadMessagesFromChannelInput,
    auth_context: Optional[AuthContext] = None
) -> GetUnreadMessagesFromChannelResult:
    """
    Get all unread messages from a specific channel.

    This tool resolves the channel identifier (name or ID) to a channel ID,
    retrieves the channel's last_read timestamp, and fetches all messages
    that were sent after that timestamp. This provides accurate unread message
    detection for the specified channel.

    Args:
        input: Parameters including channel identifier and optional timestamp
        auth_context: Authentication context

    Returns:
        Unread messages from the specified channel with metadata.
        When presenting to users, always display username/user_name fields instead
        of user_id fields for better user experience.
    """
    client = create_slack_client(auth_context)
    channel_helper = create_channel_helper(client)

    try:
        # Resolve channel identifier to channel ID
        resolved_id, suggestions = channel_helper.resolve_channel_identifier(input.channel)

        if not resolved_id:
            return GetUnreadMessagesFromChannelResult(
                success=False,
                channel_id="",
                channel_name=None,
                unread_messages=[],
                unread_count=0,
                last_read=None,
                oldest_unread_ts=None,
                message=f"Channel '{input.channel}' not found. {' '.join(suggestions) if suggestions else ''}"
            )

        # Get channel info to retrieve channel name and last_read timestamp with retry logic
        channel_info_response = _make_request_with_retry(
            client,
            "get_conversation_info",
            channel=resolved_id
        )
        if not channel_info_response.get("ok"):
            return GetUnreadMessagesFromChannelResult(
                success=False,
                channel_id=resolved_id,
                channel_name=None,
                unread_messages=[],
                unread_count=0,
                last_read=None,
                oldest_unread_ts=None,
                message=f"Failed to get channel info: {channel_info_response.get('error', 'Unknown error')}"
            )

        channel = channel_info_response.get("channel", {})
        channel_name = channel.get("name")
        last_read = channel.get("last_read")

        # Determine timestamp for fetching unread messages
        if input.since_ts:
            since_ts = input.since_ts
        elif last_read:
            since_ts = last_read
        else:
            # Fallback to 24 hours ago if no last_read timestamp
            since_ts = str(time.time() - (24 * 60 * 60))

        # Fetch messages with smart pagination strategy
        all_messages = []

        if input.limit and input.limit <= 200:
            # User specified a limit, do single fetch with retry logic
            messages_response = _make_request_with_retry(
                client,
                "get_conversation_history",
                channel=resolved_id,
                oldest=since_ts,
                limit=input.limit,
                inclusive=False  # Don't include the message at since_ts since it was already read
            )

            if not messages_response.get("ok"):
                return GetUnreadMessagesFromChannelResult(
                    success=False,
                    channel_id=resolved_id,
                    channel_name=channel_name,
                    unread_messages=[],
                    unread_count=0,
                    last_read=last_read,
                    oldest_unread_ts=None,
                    message=f"Failed to fetch messages: {messages_response.get('error', 'Unknown error')}"
                )

            all_messages = messages_response.get("messages", [])
        else:
            # No limit or high limit - use pagination for completeness
            all_messages = _paginate_conversation_history(
                client,
                channel=resolved_id,
                oldest=since_ts,
                inclusive=False
            )

        if not all_messages:
            return GetUnreadMessagesFromChannelResult(
                success=True,
                channel_id=resolved_id,
                channel_name=channel_name,
                unread_messages=[],
                unread_count=0,
                last_read=last_read,
                oldest_unread_ts=None,
                message=f"No unread messages in #{channel_name or resolved_id}"
            )

        # Batch user resolution - collect all user IDs first for efficiency
        from slack_connector.utils.user_resolver import create_user_resolver
        user_resolver = create_user_resolver(client)

        all_user_ids = set()
        for msg_data in all_messages:
            # Collect user IDs from messages
            if msg_data.get("user"):
                all_user_ids.add(msg_data["user"])
            # Collect from reactions
            for reaction in msg_data.get("reactions", []):
                all_user_ids.update(reaction.get("users", []))
            # Collect from reply users
            all_user_ids.update(msg_data.get("reply_users", []))
            # Collect parent user
            if msg_data.get("parent_user_id"):
                all_user_ids.add(msg_data["parent_user_id"])

        # Batch resolve all user IDs upfront (single cache warm-up)
        if all_user_ids:
            user_resolver.resolve_user_ids_batch(list(all_user_ids))

        # Process messages with pre-warmed user cache
        unread_messages = []
        oldest_unread_ts = None

        from slack_connector.utils.message_helpers import create_message_with_resolved_users

        for msg_data in all_messages:
            # Skip if message is older than since_ts (safety check)
            msg_ts = msg_data.get("ts", "0")
            if float(msg_ts) <= float(since_ts):
                continue

            # Add channel and permalink in message data
            msg_data["channel"] = resolved_id
            if msg_data.get("ts"):
                message_ts = msg_data["ts"].replace(".", "")
                msg_data["permalink"] = f"https://slack.com/archives/{resolved_id}/p{message_ts}"

            # Create message with resolved usernames (uses pre-warmed cache)
            message = create_message_with_resolved_users(msg_data, user_resolver)
            unread_messages.append(message)

            # Track oldest unread timestamp
            if oldest_unread_ts is None or float(msg_ts) < float(oldest_unread_ts):
                oldest_unread_ts = msg_ts

        # Sort messages chronologically (oldest first)
        unread_messages.sort(key=lambda msg: float(msg.ts or "0"))

        return GetUnreadMessagesFromChannelResult(
            success=True,
            channel_id=resolved_id,
            channel_name=channel_name,
            unread_messages=unread_messages,
            unread_count=len(unread_messages),
            last_read=last_read,
            oldest_unread_ts=oldest_unread_ts,
            message=f"Found {len(unread_messages)} unread messages in #{channel_name or resolved_id}"
        )

    except Exception as e:
        return GetUnreadMessagesFromChannelResult(
            success=False,
            channel_id=input.channel,
            channel_name=None,
            unread_messages=[],
            unread_count=0,
            last_read=None,
            oldest_unread_ts=None,
            message=f"Error retrieving unread messages from channel: {str(e)}"
        )


@slack.tool(name="get_unread_messages_from_user", desc="Get all unread direct messages from a specific user. When presenting results to users, always display username/display_name instead of user_id for better readability.")
def get_unread_messages_from_user(
    input: GetUnreadMessagesFromUserInput,
    auth_context: Optional[AuthContext] = None
) -> GetUnreadMessagesFromUserResult:
    """
    Get all unread direct messages from a specific user.
    
    This tool resolves the user identifier (ID, name, email) to a user ID,
    finds the DM conversation with that user, then fetches unread messages
    from that conversation based on the last_read timestamp.
    
    Args:
        input: Parameters including user identifier and optional timestamp
        auth_context: Authentication context
        
    Returns:
        Unread direct messages from the specified user with metadata.
        When presenting to users, always display username/user_name fields instead 
        of user_id fields for better user experience.
    """
    client = create_slack_client(auth_context)
    
    try:
        # Try to resolve user identifier to user ID
        resolved_user_id = None
        user_name = None
        
        # First, check if it's already a valid user ID (starts with U)
        if input.user.startswith('U') and len(input.user) >= 9:
            try:
                user_info_response = client.get_user_info(input.user)
                if user_info_response.get("ok"):
                    resolved_user_id = input.user
                    user_data = user_info_response.get("user", {})
                    user_name = user_data.get("profile", {}).get("display_name") or user_data.get("real_name") or user_data.get("name")
            except:
                pass
        
        # If not resolved yet, try email lookup
        if not resolved_user_id and "@" in input.user:
            try:
                email_lookup_response = client.lookup_user_by_email(input.user)
                if email_lookup_response.get("ok"):
                    user_data = email_lookup_response.get("user", {})
                    resolved_user_id = user_data.get("id")
                    user_name = user_data.get("profile", {}).get("display_name") or user_data.get("real_name") or user_data.get("name")
            except:
                pass
        
        # If still not resolved, search through users list
        if not resolved_user_id:
            try:
                # Get all users and search by name/display name
                users_response = client.list_users(limit=1000)
                if users_response.get("ok"):
                    members = users_response.get("members", [])
                    search_term = input.user.lower().strip("@")
                    
                    for member in members:
                        # Skip deleted users and bots
                        if member.get("deleted") or member.get("is_bot"):
                            continue
                            
                        # Check various name fields
                        names_to_check = [
                            member.get("name", ""),
                            member.get("real_name", ""),
                            member.get("profile", {}).get("display_name", ""),
                            member.get("profile", {}).get("real_name", "")
                        ]
                        
                        for name in names_to_check:
                            if name and name.lower() == search_term:
                                resolved_user_id = member.get("id")
                                user_name = member.get("profile", {}).get("display_name") or member.get("real_name") or member.get("name")
                                break
                        
                        if resolved_user_id:
                            break
            except:
                pass
        
        if not resolved_user_id:
            return GetUnreadMessagesFromUserResult(
                success=False,
                user_id="",
                user_name=None,
                channel_id="",
                unread_messages=[],
                unread_count=0,
                last_read=None,
                oldest_unread_ts=None,
                message=f"User '{input.user}' not found. Please provide a valid user ID, username, display name, or email address."
            )
        
        # Find the DM conversation with this user
        conversations_response = client.list_conversations(
            types="im",
            limit=1000,
            exclude_archived=True
        )
        
        if not conversations_response.get("ok"):
            return GetUnreadMessagesFromUserResult(
                success=False,
                user_id=resolved_user_id,
                user_name=user_name,
                channel_id="",
                unread_messages=[],
                unread_count=0,
                last_read=None,
                oldest_unread_ts=None,
                message=f"Failed to fetch DM conversations: {conversations_response.get('error', 'Unknown error')}"
            )
        
        # Find the DM channel with this user
        dm_channel_id = None
        dm_last_read = None
        
        for channel in conversations_response.get("channels", []):
            if channel.get("user") == resolved_user_id:
                dm_channel_id = channel.get("id")
                dm_last_read = channel.get("last_read")
                break
        
        if not dm_channel_id:
            # Try to open a DM conversation (this might create it if it doesn't exist)
            try:
                open_dm_response = client.open_conversation([resolved_user_id])
                if open_dm_response.get("ok"):
                    dm_channel_data = open_dm_response.get("channel", {})
                    dm_channel_id = dm_channel_data.get("id")
                    dm_last_read = dm_channel_data.get("last_read")
                else:
                    return GetUnreadMessagesFromUserResult(
                        success=False,
                        user_id=resolved_user_id,
                        user_name=user_name,
                        channel_id="",
                        unread_messages=[],
                        unread_count=0,
                        last_read=None,
                        oldest_unread_ts=None,
                        message=f"No DM conversation found with user {user_name or resolved_user_id} and couldn't create one"
                    )
            except Exception as e:
                return GetUnreadMessagesFromUserResult(
                    success=False,
                    user_id=resolved_user_id,
                    user_name=user_name,
                    channel_id="",
                    unread_messages=[],
                    unread_count=0,
                    last_read=None,
                    oldest_unread_ts=None,
                    message=f"Error opening DM conversation: {str(e)}"
                )
        
        # Determine the timestamp to fetch messages since
        if input.since_ts:
            since_ts = input.since_ts
        elif dm_last_read:
            since_ts = dm_last_read
        else:
            # Fallback to 24 hours ago if no last_read timestamp
            import time
            since_ts = str(time.time() - (24 * 60 * 60))
        
        # Fetch messages newer than since_ts
        messages_response = client.get_conversation_history(
            channel=dm_channel_id,
            oldest=since_ts,
            limit=input.limit,
            inclusive=False  # Don't include the message at since_ts since it was already read
        )
        
        if not messages_response.get("ok"):
            return GetUnreadMessagesFromUserResult(
                success=False,
                user_id=resolved_user_id,
                user_name=user_name,
                channel_id=dm_channel_id,
                unread_messages=[],
                unread_count=0,
                last_read=dm_last_read,
                oldest_unread_ts=None,
                message=f"Failed to fetch messages: {messages_response.get('error', 'Unknown error')}"
            )
        
        # Convert message data to Message objects
        raw_messages = messages_response.get("messages", [])
        unread_messages = []
        oldest_unread_ts = None
        
        for msg_data in raw_messages:
            # Skip if message is older than since_ts (safety check)
            msg_ts = msg_data.get("ts", "0")
            if float(msg_ts) <= float(since_ts):
                continue
                
            # Create Message object with resolved usernames
            from slack_connector.utils.message_helpers import create_message_with_resolved_users
            from slack_connector.utils.user_resolver import create_user_resolver
            if not hasattr(client, '_user_resolver'):
                client._user_resolver = create_user_resolver(client)
            
            # Set channel and permalink in message data
            msg_data["channel"] = dm_channel_id
            if msg_data.get("ts"):
                msg_data["permalink"] = f"https://slack.com/archives/{dm_channel_id}/p{msg_data['ts'].replace('.', '')}"
            
            message = create_message_with_resolved_users(msg_data, client._user_resolver)
            unread_messages.append(message)
            
            # Track oldest unread timestamp
            if oldest_unread_ts is None or float(msg_ts) < float(oldest_unread_ts):
                oldest_unread_ts = msg_ts
        
        # Sort messages chronologically (oldest first)
        unread_messages.sort(key=lambda msg: float(msg.ts or "0"))
        
        return GetUnreadMessagesFromUserResult(
            success=True,
            user_id=resolved_user_id,
            user_name=user_name,
            channel_id=dm_channel_id,
            unread_messages=unread_messages,
            unread_count=len(unread_messages),
            last_read=dm_last_read,
            oldest_unread_ts=oldest_unread_ts,
            message=f"Found {len(unread_messages)} unread messages from {user_name or resolved_user_id}"
        )
        
    except Exception as e:
        return GetUnreadMessagesFromUserResult(
            success=False,
            user_id=input.user,
            user_name=None,
            channel_id="",
            unread_messages=[],
            unread_count=0,
            last_read=None,
            oldest_unread_ts=None,
            message=f"Error retrieving unread messages from user: {str(e)}"
        )