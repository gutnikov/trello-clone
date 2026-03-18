import { Link } from "@tanstack/react-router";
import { Separator } from "#/components/ui/separator";
import { cn } from "#/lib/utils";
import ThemeToggle from "./ThemeToggle";

const navLinkClass =
  "inline-flex items-center rounded-lg px-2.5 py-1.5 text-sm font-medium text-muted-foreground no-underline transition-colors hover:bg-muted hover:text-foreground";
const navLinkActiveClass = "bg-accent text-accent-foreground";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-lg">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link to="/" className="text-sm font-semibold tracking-tight text-foreground no-underline">
          trello-clone
        </Link>

        <div className="flex items-center gap-1">
          <Link
            to="/"
            className={navLinkClass}
            activeProps={{ className: cn(navLinkClass, navLinkActiveClass) }}
          >
            Home
          </Link>
          <Link
            to="/about"
            className={navLinkClass}
            activeProps={{ className: cn(navLinkClass, navLinkActiveClass) }}
          >
            About
          </Link>
          <Separator orientation="vertical" className="mx-1 h-5" />
          <ThemeToggle />
        </div>
      </nav>
    </header>
  );
}
