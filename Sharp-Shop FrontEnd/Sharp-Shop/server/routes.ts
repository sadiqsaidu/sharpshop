import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  app.get("/api/products", async (_req, res) => {
    try {
      const products = await storage.getAllProducts();
      res.json(products);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch products" });
    }
  });

  app.get("/api/products/:id", async (req, res) => {
    try {
      const product = await storage.getProduct(req.params.id);
      if (!product) {
        return res.status(404).json({ message: "Product not found" });
      }
      res.json(product);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch product" });
    }
  });

  app.patch("/api/products/:id/stock", async (req, res) => {
    try {
      const { quantity } = req.body;
      if (typeof quantity !== "number" || quantity < 0) {
        return res.status(400).json({ message: "Invalid quantity" });
      }
      
      const product = await storage.updateProductStock(req.params.id, quantity);
      if (!product) {
        return res.status(404).json({ message: "Product not found" });
      }
      res.json(product);
    } catch (error) {
      res.status(500).json({ message: "Failed to update stock" });
    }
  });

  app.get("/api/products/trader/:traderId", async (req, res) => {
    try {
      const products = await storage.getProductsByTrader(req.params.traderId);
      res.json(products);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch trader products" });
    }
  });

  // Trader routes
  app.get("/api/trader/me", async (req, res) => {
    if (!req.isAuthenticated()) {
      return res.status(401).json({ message: "Unauthorized" });
    }
    try {
      const trader = await storage.getTraderByUserId(req.user!.id);
      if (!trader) {
        return res.status(404).json({ message: "Trader profile not found" });
      }
      res.json(trader);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch trader profile" });
    }
  });

  app.get("/api/traders/:traderId", async (req, res) => {
    try {
      const trader = await storage.getTrader(req.params.traderId);
      if (!trader) {
        return res.status(404).json({ message: "Trader not found" });
      }
      res.json(trader);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch trader" });
    }
  });

  // Comment routes
  app.get("/api/comments/:productId", async (req, res) => {
    try {
      const comments = await storage.getCommentsByProduct(req.params.productId);
      res.json(comments);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch comments" });
    }
  });

  app.post("/api/comments", async (req, res) => {
    try {
      const comment = await storage.createComment(req.body);
      res.status(201).json(comment);
    } catch (error) {
      res.status(500).json({ message: "Failed to create comment" });
    }
  });

  app.delete("/api/comments/:id", async (req, res) => {
    try {
      const success = await storage.deleteComment(req.params.id);
      if (!success) {
        return res.status(404).json({ message: "Comment not found" });
      }
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: "Failed to delete comment" });
    }
  });

  // Favorite routes
  app.get("/api/favorites/:userId", async (req, res) => {
    try {
      const favorites = await storage.getFavoritesByUser(req.params.userId);
      res.json(favorites);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch favorites" });
    }
  });

  app.post("/api/favorites", async (req, res) => {
    try {
      const favorite = await storage.createFavorite(req.body);
      res.status(201).json(favorite);
    } catch (error) {
      res.status(500).json({ message: "Failed to add favorite" });
    }
  });

  app.delete("/api/favorites", async (req, res) => {
    try {
      const { productId, userId } = req.body;
      const success = await storage.deleteFavorite(productId, userId);
      if (!success) {
        return res.status(404).json({ message: "Favorite not found" });
      }
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: "Failed to remove favorite" });
    }
  });

  app.get("/api/favorites/check/:productId/:userId", async (req, res) => {
    try {
      const isFavorite = await storage.isFavorite(req.params.productId, req.params.userId);
      res.json({ isFavorite });
    } catch (error) {
      res.status(500).json({ message: "Failed to check favorite status" });
    }
  });

  // Like routes
  app.get("/api/likes/count/:productId", async (req, res) => {
    try {
      const count = await storage.getLikeCount(req.params.productId);
      res.json({ count });
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch like count" });
    }
  });

  app.get("/api/likes/check/:productId/:userId", async (req, res) => {
    try {
      const isLiked = await storage.isLiked(req.params.productId, req.params.userId);
      res.json({ isLiked });
    } catch (error) {
      res.status(500).json({ message: "Failed to check like status" });
    }
  });

  app.post("/api/likes", async (req, res) => {
    try {
      const like = await storage.createLike(req.body);
      res.status(201).json(like);
    } catch (error) {
      res.status(500).json({ message: "Failed to add like" });
    }
  });

  app.delete("/api/likes", async (req, res) => {
    try {
      const { productId, userId } = req.body;
      const success = await storage.deleteLike(productId, userId);
      if (!success) {
        return res.status(404).json({ message: "Like not found" });
      }
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: "Failed to remove like" });
    }
  });

  return httpServer;
}
