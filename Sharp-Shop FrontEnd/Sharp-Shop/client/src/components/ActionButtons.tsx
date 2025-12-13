import { Button } from "@/components/ui/button";
import { ShoppingBag, Share2, Plus } from "lucide-react";
import { SiWhatsapp } from "react-icons/si";

interface ActionButtonsProps {
  productName: string;
  productUrl?: string;
  whatsappNumber?: string | null;
  isSoldOut: boolean;
  onBuyClick: () => void;
  userRole?: string | null;
}

export function ActionButtons({
  productName,
  productUrl,
  whatsappNumber,
  isSoldOut,
  onBuyClick,
  userRole,
}: ActionButtonsProps) {
  const handleShare = async () => {
    const shareData = {
      title: productName,
      text: `Check out ${productName} on SharpShop!`,
      url: productUrl || window.location.href,
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        await navigator.clipboard.writeText(shareData.url);
      }
    } catch (err) {
      console.log("Share failed:", err);
    }
  };

  const handleWhatsApp = () => {
    if (userRole === "seller") {
      // Sellers upload products
      window.open(
        "https://wa.me/14155238886?text=Hi,%20I%20want%20to%20add%20a%20product",
        "_blank"
      );
    } else {
      // Buyers contact seller
      const phoneNumber = whatsappNumber || "2348174930608";
      const message = encodeURIComponent(
        `Hello! I saw this product on SharpShop and I'm interested: *${productName}*. Is it still available?`
      );
      window.open(`https://wa.me/${phoneNumber}?text=${message}`, "_blank");
    }
  };

  return (
    <div className="flex items-center gap-3 w-full">
      <Button
        data-testid="button-buy-now"
        onClick={onBuyClick}
        disabled={isSoldOut}
        className="flex-1 h-12 text-base font-semibold bg-white/20 backdrop-blur-md border border-white/30 text-white gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        variant="ghost"
      >
        <ShoppingBag className="w-5 h-5" />
        {isSoldOut ? "Sold Out" : "Buy Now"}
      </Button>

      <Button
        data-testid="button-share"
        onClick={handleShare}
        size="icon"
        variant="ghost"
        className="h-12 w-12 bg-white/10 backdrop-blur-md border border-white/20 text-white"
      >
        <Share2 className="w-5 h-5" />
      </Button>

      {userRole === "seller" && (
        <Button
          data-testid="button-whatsapp"
          onClick={handleWhatsApp}
          size="icon"
          variant="ghost"
          className="h-12 w-12 bg-emerald-500/80 backdrop-blur-md border border-emerald-400/50 text-white relative"
        >
          <SiWhatsapp className="w-5 h-5" />
          <Plus className="w-3 h-3 absolute -top-0.5 -right-0.5 bg-emerald-700 rounded-full p-0.5" />
        </Button>
      )}
    </div>
  );
}
