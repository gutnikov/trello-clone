import { Link } from "@tanstack/react-router";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-[var(--line)] bg-[var(--header-bg)] px-4 backdrop-blur-lg">
      <nav className="page-wrap flex items-center justify-between py-3">
        <Link
          to="/"
          className="text-sm font-semibold tracking-tight text-[var(--sea-ink)] no-underline"
        >
          trello-clone
        </Link>

        <div className="flex items-center gap-4 text-sm font-semibold">
          <Link to="/" className="nav-link" activeProps={{ className: "nav-link is-active" }}>
            Home
          </Link>
          <Link to="/about" className="nav-link" activeProps={{ className: "nav-link is-active" }}>
            About
          </Link>
          <ThemeToggle />
        </div>
      </nav>
    </header>
  );
}
