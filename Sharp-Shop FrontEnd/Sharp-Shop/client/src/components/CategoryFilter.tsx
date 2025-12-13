import { Badge } from "@/components/ui/badge";
import { PRODUCT_CATEGORIES, type ProductCategory } from "@shared/schema";

interface CategoryFilterProps {
  selected: ProductCategory | null;
  onSelect: (category: ProductCategory | null) => void;
}

export function CategoryFilter({ selected, onSelect }: CategoryFilterProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
      <Badge
        data-testid="filter-category-all"
        onClick={() => onSelect(null)}
        className={`cursor-pointer whitespace-nowrap px-3 py-1.5 ${
          selected === null
            ? "bg-white text-black"
            : "bg-white/10 text-white border-white/20"
        }`}
      >
        All
      </Badge>
      {PRODUCT_CATEGORIES.map((category) => (
        <Badge
          key={category}
          data-testid={`filter-category-${category.toLowerCase().replace(/\s+/g, "-")}`}
          onClick={() => onSelect(category)}
          className={`cursor-pointer whitespace-nowrap px-3 py-1.5 ${
            selected === category
              ? "bg-white text-black"
              : "bg-white/10 text-white border-white/20"
          }`}
        >
          {category}
        </Badge>
      ))}
    </div>
  );
}
