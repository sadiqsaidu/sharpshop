import { useQuery } from "@tanstack/react-query";
import { type Product, type Trader } from "@shared/schema";
import { ProductSkeleton } from "@/components/ProductSkeleton";
import { useAuth } from "@/contexts/AuthContext";
import {
  ArrowLeft,
  MapPin,
  Mail,
  MoreHorizontal,
  Share2,
  ChevronDown,
  Star,
  UserPlus,
  AlertCircle,
  RefreshCw,
  X,
  Eye,
  Phone
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Link, useParams, useLocation } from "wouter";
import { motion, AnimatePresence } from "framer-motion";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useState } from "react";
import { CustomerChat } from "@/components/CustomerChat";

const SUGGESTED_TRADERS = [
  { id: "trader_001", name: "SneakerHub NG", category: "Footwear" },
  { id: "trader_002", name: "VintageVibes Lagos", category: "Fashion" },
  { id: "trader_003", name: "LuxeAccessories", category: "Accessories" },
  { id: "trader_004", name: "TimePiece Gallery", category: "Watches" },
];

export default function TraderProfile() {
  const [, setLocation] = useLocation();
  const params = useParams<{ traderId: string }>();
  const [isExpanded, setIsExpanded] = useState(false);
  const traderId = params.traderId;
  const { user } = useAuth();

  const {
    data: trader,
    isLoading: traderLoading,
    isError: traderError,
  } = useQuery<Trader>({
    queryKey: ["/api/traders", traderId],
    enabled: !!traderId,
  });

  const {
    data: products,
    isLoading,
    isError,
    refetch,
  } = useQuery<Product[]>({
    queryKey: ["/api/products/trader", traderId],
    enabled: !!traderId,
  });

  const traderName = trader?.businessName || products?.[0]?.traderName || "Trader";
  const username = traderName.toLowerCase().replace(/\s+/g, '') + "_official";
  const bio = trader?.bio || "Quality products at affordable prices. 🇳🇬";
  const location = trader?.address || "Nigeria";
  const whatsapp = trader?.whatsappNumber;
  const followers = "158.5K"; // TODO: Implement follower count

  if (isLoading || traderLoading) {
    return (
      <div className="h-screen w-full bg-black flex items-center justify-center">
        <div className="absolute inset-0 hidden md:block bg-gradient-to-br from-neutral-900 via-black to-neutral-900" />
        <div className="absolute inset-0 hidden md:block backdrop-blur-sm bg-black/60" />

        <div className="relative w-full h-full md:max-w-[430px] md:h-[90vh] md:max-h-[900px] md:rounded-2xl md:overflow-hidden md:shadow-2xl md:shadow-black/50 md:border md:border-white/10 bg-black">
          <ProductSkeleton />
        </div>
      </div>
    );
  }

  if (isError || traderError) {
    return (
      <div className="h-screen w-full bg-black flex items-center justify-center">
        <div className="absolute inset-0 hidden md:block bg-gradient-to-br from-neutral-900 via-black to-neutral-900" />
        <div className="absolute inset-0 hidden md:block backdrop-blur-sm bg-black/60" />

        <div className="relative w-full h-full md:max-w-[430px] md:h-[90vh] md:max-h-[900px] md:rounded-2xl md:overflow-hidden md:shadow-2xl md:shadow-black/50 md:border md:border-white/10 bg-black flex flex-col items-center justify-center p-6">
          <AlertCircle className="w-16 h-16 text-red-500 mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Something went wrong</h2>
          <p className="text-white/70 text-center mb-6">
            We couldn't load this trader's products. Please try again.
          </p>
          <Button
            data-testid="button-retry"
            onClick={() => refetch()}
            variant="outline"
            className="gap-2 bg-white/10 border-white/20 text-white"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className="h-screen w-full bg-black flex items-center justify-center"
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.2}
      onDragEnd={(_, { offset }) => {
        if (offset.x > 50) {
          setLocation("/");
        }
      }}
    >
      <div className="absolute inset-0 hidden md:block bg-gradient-to-br from-neutral-900 via-black to-neutral-900" />
      <div className="absolute inset-0 hidden md:block backdrop-blur-sm bg-black/60" />

      <div className="relative w-full h-full md:max-w-[430px] md:h-[90vh] md:max-h-[900px] md:rounded-2xl md:overflow-hidden md:shadow-2xl md:shadow-black/50 md:border md:border-white/10 bg-[#121212] flex flex-col overflow-y-auto scrollbar-hide">

        {/* Header Image & Nav */}
        <div className="relative h-48 w-full shrink-0">
          {/* Background Image */}
          <div className="absolute inset-0 bg-neutral-800">
            <img
              src={products?.[0]?.imageUrl || "https://images.unsplash.com/photo-1557683316-973673baf926"}
              alt="Cover"
              className="w-full h-full object-cover opacity-60"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-[#121212]" />
          </div>

          {/* Top Nav */}
          <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-center z-10">
            <Link href="/">
              <Button size="icon" variant="secondary" className="h-10 w-10 rounded-full bg-black/40 backdrop-blur-md border-none text-white hover:bg-black/60">
                <ArrowLeft className="w-6 h-6" />
              </Button>
            </Link>
            <div className="flex gap-2">
              <Button size="icon" variant="secondary" className="h-10 w-10 rounded-full bg-black/40 backdrop-blur-md border-none text-white hover:bg-black/60">
                <Share2 className="w-5 h-5" />
              </Button>
              <Button size="icon" variant="secondary" className="h-10 w-10 rounded-full bg-black/40 backdrop-blur-md border-none text-white hover:bg-black/60">
                <MoreHorizontal className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Profile Info */}
        <div className="px-4 -mt-12 relative z-10 flex-1 flex flex-col">
          <div className="flex items-end gap-4 mb-4">
            <Avatar className="w-24 h-24 border-4 border-[#121212] shadow-xl">
              <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${traderName}`} />
              <AvatarFallback className="bg-primary text-white text-2xl">{traderName[0]}</AvatarFallback>
            </Avatar>
            <div className="pb-2 flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-white truncate">{traderName}</h1>
                <div className="bg-emerald-500 rounded-full p-0.5">
                  <Star className="w-3 h-3 fill-white text-white" />
                </div>
              </div>
              <p className="text-xs text-white/60 line-clamp-1">
                {username} • {followers}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 mb-4">
            {whatsapp && (
              <Button
                onClick={() => window.open(`https://wa.me/${whatsapp.replace(/[^0-9]/g, '')}`, '_blank')}
                className="flex-1 bg-green-500 hover:bg-green-600 text-white font-bold rounded-full h-10 text-base"
              >
                <Phone className="w-5 h-5 mr-2" />
                WhatsApp
              </Button>
            )}
            <Button className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-full h-10 text-base">
              <UserPlus className="w-5 h-5 mr-2" />
              Follow
            </Button>

            <Button
              size="icon"
              variant="secondary"
              className={`h-10 w-10 rounded-full bg-white/10 border-none text-white hover:bg-white/20 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
              onClick={() => setIsExpanded(!isExpanded)}
            >
              <ChevronDown className="w-6 h-6" />
            </Button>
          </div>

          {/* Expansion Content */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="overflow-hidden mb-4"
              >
                <div className="py-2">
                  <p className="text-base font-semibold text-white mb-3 px-1">Recommended Accounts</p>
                  <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide -mx-4 px-4">
                    {SUGGESTED_TRADERS.filter(t => t.id !== traderId).map((trader) => (
                      <div
                        key={trader.id}
                        className="flex flex-col items-center p-4 rounded-2xl bg-[#1E1E1E] min-w-[140px] w-[140px] relative shrink-0"
                      >
                        <button className="absolute top-2 right-2 text-white/40 hover:text-white">
                          <X className="w-4 h-4" />
                        </button>

                        <div className="relative mb-3 mt-2">
                          <Avatar className="h-16 w-16 border-none">
                            <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${trader.name}`} />
                            <AvatarFallback>{trader.name[0]}</AvatarFallback>
                          </Avatar>
                          <div className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 rounded-full border-2 border-[#1E1E1E]" />
                        </div>

                        <h3 className="font-semibold text-white text-sm text-center truncate w-full mb-1">{trader.name}</h3>
                        <p className="text-[10px] text-white/50 text-center mb-4">{trader.category}</p>

                        <Button
                          size="sm"
                          className="w-full h-8 rounded-full bg-white/10 hover:bg-white/20 text-white text-xs font-medium gap-1.5"
                          onClick={() => setLocation(`/trader/${trader.id}`)}
                        >
                          <Eye className="w-3.5 h-3.5" />
                          View
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Info Buttons */}
          <div className="flex gap-3 mb-4 overflow-x-auto scrollbar-hide">
            <Button variant="outline" size="sm" className="rounded-full bg-white/5 border-white/10 text-white/80 hover:bg-white/10 hover:text-white h-8 text-xs">
              <MapPin className="w-3 h-3 mr-2" />
              {location}
            </Button>
            <Button variant="outline" size="sm" className="rounded-full bg-white/5 border-white/10 text-white/80 hover:bg-white/10 hover:text-white h-8 text-xs">
              <Mail className="w-3 h-3 mr-2" />
              Contact
            </Button>
          </div>

          {/* Bio */}
          <p className="text-white/90 mb-6 text-sm leading-relaxed">
            {bio}
          </p>

          {/* Tabs */}
          <Tabs defaultValue="stories" className="w-full flex-1 flex flex-col">
            <TabsList className="w-full bg-transparent border-b border-white/10 p-0 h-auto rounded-none shrink-0">
              <TabsTrigger
                value="stories"
                className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-emerald-500 data-[state=active]:bg-transparent data-[state=active]:text-emerald-500 text-white/60 pb-3 font-bold text-sm uppercase tracking-wide"
              >
                Products
              </TabsTrigger>
              <TabsTrigger
                value="spotlight"
                className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-emerald-500 data-[state=active]:bg-transparent data-[state=active]:text-emerald-500 text-white/60 pb-3 font-bold text-sm uppercase tracking-wide"
              >
                Spotlight
              </TabsTrigger>
            </TabsList>

            <TabsContent value="stories" className="mt-0 flex-1">
              <div className="grid grid-cols-3 gap-0.5 pb-20">
                {products?.map((product) => (
                  <div key={product.id} className="aspect-[3/4] relative bg-white/5 group cursor-pointer overflow-hidden">
                    <img
                      src={product.imageUrl}
                      alt={product.name}
                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                    />
                    <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/80 to-transparent">
                      <p className="text-white text-[10px] font-bold truncate">{product.name}</p>
                    </div>
                  </div>
                ))}
                {/* Fill with placeholders if few products */}
                {Array.from({ length: Math.max(0, 9 - (products?.length || 0)) }).map((_, i) => (
                  <div key={`placeholder-${i}`} className="aspect-[3/4] bg-white/5" />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="spotlight" className="mt-0 flex-1">
              <div className="flex flex-col items-center justify-center py-12 text-white/50 h-full">
                <Star className="w-12 h-12 mb-4 opacity-20" />
                <p>No spotlight content yet</p>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Customer Assistant Chat */}
      {traderId && <CustomerChat traderId={traderId} traderName={traderName} />}
    </motion.div>
  );
}
