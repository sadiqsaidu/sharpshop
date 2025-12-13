import { useState } from "react";
import { Heart, Send, X } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { useAuth } from "@/contexts/AuthContext";

interface Comment {
  id: string;
  productId: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  content: string;
  emojiReaction?: string;
  createdAt: string;
}

const EMOJIS = ["❤️", "😍", "😂", "😭", "🔥", "🙏", "😊"];

// Generate a consistent guest ID from browser fingerprint or localStorage
const getGuestId = () => {
  let userId = localStorage.getItem('sharpshop_guest_id');
  if (!userId) {
    userId = 'guest_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('sharpshop_guest_id', userId);
  }
  return userId;
};

const getGuestName = () => {
  let userName = localStorage.getItem('sharpshop_guest_name');
  if (!userName) {
    const names = ['Chioma', 'Emeka', 'Fatima', 'Tunde', 'Ngozi', 'Ade', 'Kemi', 'Chidi'];
    userName = names[Math.floor(Math.random() * names.length)];
    localStorage.setItem('sharpshop_guest_name', userName);
  }
  return userName;
};

interface CommentSectionProps {
  children?: React.ReactNode;
  trigger?: (count: number) => React.ReactNode;
  productId: string;
}

export function CommentSection({ children, trigger, productId }: CommentSectionProps) {
  const [newComment, setNewComment] = useState("");
  const queryClient = useQueryClient();
  const { user } = useAuth();
  
  const userId = user?.id || getGuestId();
  const userName = user?.username || getGuestName();

  // Fetch comments from API
  const { data: comments = [], isLoading } = useQuery({
    queryKey: ['comments', productId],
    queryFn: async () => {
      const res = await fetch(`/api/comments/${productId}`);
      if (!res.ok) throw new Error('Failed to fetch comments');
      return res.json() as Promise<Comment[]>;
    },
  });

  // Add comment mutation
  const addCommentMutation = useMutation({
    mutationFn: async (content: string) => {
      const res = await fetch('/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          productId,
          userId,
          userName,
          userAvatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${userId}`,
          content,
        }),
      });
      if (!res.ok) throw new Error('Failed to add comment');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', productId] });
      setNewComment("");
    },
  });

  const handleAddComment = () => {
    if (!newComment.trim()) return;
    addCommentMutation.mutate(newComment);
  };

  return (
    <Drawer>
      <DrawerTrigger asChild>{trigger ? trigger(comments.length) : children}</DrawerTrigger>
      <DrawerContent className="h-[75vh] bg-[#121212] border-t border-white/10 text-white">
        <DrawerHeader className="border-b border-white/10 pb-4 pt-2">
          <div className="flex items-center justify-center">
            <DrawerTitle className="text-center text-sm">
              Comments
            </DrawerTitle>
          </div>
        </DrawerHeader>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-6">
            {isLoading ? (
              <div className="text-center text-white/50 py-8">Loading comments...</div>
            ) : comments.length === 0 ? (
              <div className="text-center text-white/50 py-8">
                No comments yet. Be the first to comment!
              </div>
            ) : (
              comments.map((comment) => (
                <div key={comment.id} className="flex gap-3">
                  <Avatar className="h-8 w-8 border-none">
                    <AvatarImage src={comment.userAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${comment.userId}`} />
                    <AvatarFallback>{comment.userName[0]}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-baseline gap-2">
                      <span className="text-xs font-semibold text-white/90">
                        {comment.userName}
                      </span>
                      <span className="text-[10px] text-white/50">
                        {formatDistanceToNow(new Date(comment.createdAt), { addSuffix: true })}
                      </span>
                    </div>
                    <p className="text-sm text-white/90 leading-snug">
                      {comment.content}
                    </p>
                    <button className="text-xs text-white/50 font-medium hover:text-white/80">
                      Reply
                    </button>
                  </div>
                  {comment.emojiReaction && (
                    <div className="text-lg">
                      {comment.emojiReaction}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </ScrollArea>

        <div className="p-4 border-t border-white/10 bg-[#121212]">
          <div className="flex justify-between mb-3 px-2">
            {EMOJIS.map((emoji) => (
              <button
                key={emoji}
                onClick={() => setNewComment((prev) => prev + emoji)}
                className="text-2xl hover:scale-110 transition-transform"
              >
                {emoji}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <Avatar className="h-8 w-8 border-none">
              <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${userId}`} />
              <AvatarFallback>{userName[0]}</AvatarFallback>
            </Avatar>
            <div className="flex-1 relative">
              <Input
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                className="bg-white/10 border-none text-white placeholder:text-white/50 pr-10 h-10 rounded-full focus-visible:ring-1 focus-visible:ring-white/20"
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleAddComment();
                }}
                disabled={addCommentMutation.isPending}
              />
              <button className="absolute right-3 top-1/2 -translate-y-1/2 text-white/70 hover:text-white">
                @
              </button>
            </div>
            {newComment && (
              <Button
                size="icon"
                onClick={handleAddComment}
                disabled={addCommentMutation.isPending}
                className="h-10 w-10 rounded-full bg-primary text-white hover:bg-primary/90"
              >
                <Send className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
