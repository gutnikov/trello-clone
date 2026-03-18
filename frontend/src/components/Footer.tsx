export default function Footer() {
  return (
    <footer className="border-t border-[var(--line)] px-4 py-6 text-center text-xs text-[var(--sea-ink-soft)]">
      &copy; {new Date().getFullYear()}
    </footer>
  );
}
