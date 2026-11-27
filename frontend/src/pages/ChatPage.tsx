import ChatWindow from "../components/chat/ChatWindow";
import SessionPanel from "../components/chat/SessionPanel";
import { useChat } from "../hooks/useChat";

export default function ChatPage() {
  const chat = useChat();

  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_300px]">
      <ChatWindow
        items={chat.items}
        language={chat.language}
        loading={chat.loading}
        error={chat.error}
        onSend={chat.send}
        onChangeLanguage={chat.changeLanguage}
        onRetry={chat.retry}
        onFeedback={chat.giveFeedback}
      />
      <SessionPanel
        clientId={chat.clientId}
        state={chat.state}
        language={chat.language}
        consent={chat.consent}
        loading={chat.loading}
        onNewFarmer={chat.startNewFarmer}
        onSend={chat.send}
      />
    </div>
  );
}
