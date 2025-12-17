import { useState, useRef, useEffect } from "react";
import { Send, MessageCircle, X, Loader2, ShoppingBag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { motion, AnimatePresence } from "framer-motion";

interface CustomerChatProps {
  traderId: string;
  traderName: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Product {
  id: string;
  name: string;
  price: number;
  image_url?: string;
}

// Use environment variable or default to backend URL
const API_Base = import.meta.env.VITE_CHAT_API_URL || "http://localhost:8000";

export function CustomerChat({ traderId, traderName }: CustomerChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMsg = inputValue;
    setInputValue("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_Base}/api/chat/customer`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          trader_id: traderId,
          message: userMsg,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();
      
      if (data.session_id) {
        setSessionId(data.session_id);
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
      
      if (data.products && data.products.length > 0) {
          // Add products to state to show in a carousel or list?
          // For now, let's just append a system message with products or render them specially
          // The backend reply usually mentions them, but we can also show a "card".
          // Let's rely on the text reply for now, but if we wanted to be fancy we could render cards.
          // Spec said "products" list is returned.
          setProducts(data.products); 
      }

    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I'm having trouble connecting right now." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <motion.div
        className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-50"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
      >
        {!isOpen && (
          <Button
            onClick={() => setIsOpen(true)}
            size="icon"
            className="h-12 w-12 md:h-14 md:w-14 rounded-full bg-black hover:bg-neutral-900 text-white shadow-lg border border-white/20"
          >
            <MessageCircle className="h-6 w-6 md:h-8 md:w-8" />
          </Button>
        )}
      </motion.div>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.9 }}
            className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-50 w-[calc(100vw-2rem)] md:w-[360px] h-[320px] bg-[#1a1a1a] border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="p-4 bg-[#222] border-b border-white/10 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10 border border-white/10">
                  <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${traderName}`} />
                  <AvatarFallback>AI</AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="font-bold text-white text-sm">{traderName} Assistant</h3>
                  <p className="text-xs text-green-400 flex items-center gap-1">
                    <span className="block w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                    Online
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white/50 hover:text-white hover:bg-white/10"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            {/* Messages Area */}
            <ScrollArea className="flex-1 p-4 bg-[#121212]">
              <div className="space-y-4">
                 {/* Welcome Message */}
                 <div className="flex gap-3">
                    <Avatar className="h-8 w-8 mt-1 border border-white/10">
                        <AvatarFallback className="bg-emerald-500 text-white text-xs">AI</AvatarFallback>
                    </Avatar>
                    <div className="bg-[#222] p-3 rounded-2xl rounded-tl-none text-white/90 text-sm max-w-[80%] border border-white/5">
                        <p>Hello! I'm here to help you verify products and check availability. What are you looking for today?</p>
                    </div>
                 </div>

                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
                  >
                    {msg.role === "assistant" && (
                        <Avatar className="h-8 w-8 mt-1 border border-white/10">
                            <AvatarFallback className="bg-emerald-500 text-white text-xs">AI</AvatarFallback>
                        </Avatar>
                    )}
                    
                    <div
                      className={`p-3 rounded-2xl text-sm max-w-[80%] ${
                        msg.role === "user"
                          ? "!bg-black text-white rounded-tr-none font-medium border border-white/20"
                          : "bg-[#222] text-white/90 rounded-tl-none border border-white/5 whitespace-pre-wrap"
                      }`}
                    >
                      {msg.content}
                    </div>
                  </motion.div>
                ))}
                
                {isLoading && (
                   <div className="flex gap-3">
                        <Avatar className="h-8 w-8 mt-1 border border-white/10">
                            <AvatarFallback className="bg-emerald-500 text-white text-xs">AI</AvatarFallback>
                        </Avatar>
                        <div className="bg-[#222] p-3 rounded-2xl rounded-tl-none border border-white/5">
                            <Loader2 className="h-4 w-4 animate-spin text-white/50" />
                        </div>
                   </div>
                )}
                <div ref={scrollRef} />
              </div>
            </ScrollArea>
           
            {/* Products Recommendation Strip (if any) */}
            {products.length > 0 && (
                <div className="bg-[#1a1a1a] border-t border-white/10 p-2 overflow-x-auto whitespace-nowrap scrollbar-hide">
                    {products.map(p => (
                        <div key={p.id} className="inline-block w-32 mr-2 bg-[#222] rounded-lg p-2 border border-white/5 align-top">
                            <div className="h-20 bg-black/20 rounded mb-2 overflow-hidden">
                                {p.image_url ? (
                                    <img src={p.image_url} alt={p.name} className="w-full h-full object-cover" />
                                ) : (
                                    <ShoppingBag className="w-full h-full p-6 text-white/20" />
                                )}
                            </div>
                            <p className="text-white text-xs truncate font-medium">{p.name}</p>
                            <p className="text-emerald-500 text-xs text font-bold">₦{p.price.toLocaleString()}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Input Area */}
            <div className="p-3 bg-[#222] border-t border-white/10 flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Ask about products..."
                className="bg-[#121212] border-white/10 text-white placeholder:text-white/30 focus-visible:ring-emerald-500"
              />
              <Button 
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                size="icon"
                className="bg-emerald-500 hover:bg-emerald-600 text-white"
              >
                <Send className="h-5 w-5" />
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
