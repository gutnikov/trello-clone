export default function Footer() {
  return (
    <footer className="border-t border-border px-6 py-6 text-center text-xs text-muted-foreground">
      &copy; {new Date().getFullYear()} trello-clone
    </footer>
  );
}
