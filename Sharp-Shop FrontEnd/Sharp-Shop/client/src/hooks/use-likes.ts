import { useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/lib/supabase";

// Generate a consistent guest ID from localStorage
const getGuestId = () => {
  let userId = localStorage.getItem('sharpshop_guest_id');
  if (!userId) {
    userId = 'guest_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('sharpshop_guest_id', userId);
  }
  return userId;
};

export function useLikes(productId: string) {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const userId = user?.id ? String(user.id) : getGuestId();

  // Set up real-time subscription for likes on this product
  useEffect(() => {
    const channel = supabase
      .channel(`likes-${productId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'likes',
          filter: `product_id=eq.${productId}`
        },
        () => {
          queryClient.invalidateQueries({ queryKey: ['likes', productId] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [productId, queryClient]);

  // Fetch like count and user's like status
  const { data: likesData } = useQuery({
    queryKey: ['likes', productId],
    queryFn: async () => {
      const [countRes, statusRes] = await Promise.all([
        fetch(`/api/likes/count/${productId}`),
        fetch(`/api/likes/check/${productId}/${userId}`)
      ]);
      
      const count = await countRes.json();
      const status = await statusRes.json();
      
      return {
        count: count.count || 0,
        isLiked: status.isLiked || false
      };
    },
  });

  const likeCount = likesData?.count ?? 0;
  const isLiked = likesData?.isLiked ?? false;

  // Toggle like mutation
  const toggleLikeMutation = useMutation({
    mutationFn: async () => {
      if (isLiked) {
        // Unlike
        const res = await fetch('/api/likes', {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ productId, userId }),
        });
        if (!res.ok) throw new Error('Failed to unlike');
      } else {
        // Like
        const res = await fetch('/api/likes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ productId, userId }),
        });
        if (!res.ok) throw new Error('Failed to like');
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['likes', productId] });
    },
  });

  const toggleLike = () => {
    toggleLikeMutation.mutate();
  };

  return {
    likeCount,
    isLiked,
    toggleLike,
  };
}
