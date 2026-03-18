import { createFileRoute } from "@tanstack/react-router";
import { ArrowRight, Kanban, Layers, Users, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  return (
    <main className="min-h-[calc(100dvh-4rem)]">
      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-20 pt-24 sm:pt-32">
        {/* Subtle background glow */}
        <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-32 left-1/2 h-[480px] w-[720px] -translate-x-1/2 rounded-full bg-primary/10 blur-3xl" />
          <div className="absolute -right-24 top-48 h-[320px] w-[320px] rounded-full bg-secondary/15 blur-3xl" />
        </div>

        <div className="rise-in mx-auto max-w-3xl text-center">
          <Badge variant="secondary" className="mb-6">
            Open Source
          </Badge>
          <h1 className="mb-6 text-4xl font-bold tracking-tight text-foreground sm:text-6xl lg:text-7xl">
            Organize your work, <span className="text-primary">visually</span>
          </h1>
          <p className="mx-auto mb-10 max-w-xl text-lg text-muted-foreground">
            A modern Kanban board built with React, TanStack, and shadcn/ui. Drag, drop, and
            collaborate — all in one place.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Button size="lg">
              Get Started
              <ArrowRight className="ml-1 size-4" />
            </Button>
            <Button variant="outline" size="lg">
              View Demo
            </Button>
          </div>
        </div>
      </section>

      <Separator className="mx-auto max-w-5xl" />

      {/* Features */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="rise-in mb-12 text-center" style={{ animationDelay: "100ms" }}>
            <h2 className="mb-3 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              Everything you need
            </h2>
            <p className="text-muted-foreground">
              Simple tools to keep your projects moving forward.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, i) => (
              <Card
                key={feature.title}
                className="rise-in group transition-shadow hover:shadow-lg"
                style={{ animationDelay: `${150 + i * 60}ms` }}
              >
                <CardHeader>
                  <div className="mb-2 flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                    <feature.icon className="size-5" />
                  </div>
                  <CardTitle className="text-base">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>{feature.description}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 pb-24 pt-8">
        <div className="rise-in mx-auto max-w-2xl text-center" style={{ animationDelay: "400ms" }}>
          <Card className="border-primary/20 bg-primary/5">
            <CardContent className="p-8 sm:p-12">
              <h3 className="mb-3 text-xl font-bold tracking-tight text-foreground sm:text-2xl">
                Ready to get organized?
              </h3>
              <p className="mb-6 text-muted-foreground">
                Start managing your projects with a clean, visual workflow.
              </p>
              <Button size="lg">
                Create your first board
                <ArrowRight className="ml-1 size-4" />
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
}

const features = [
  {
    icon: Kanban,
    title: "Kanban Boards",
    description: "Visualize work with customizable columns and drag-and-drop cards.",
  },
  {
    icon: Layers,
    title: "Multiple Lists",
    description: "Create as many lists as you need to organize tasks your way.",
  },
  {
    icon: Zap,
    title: "Real-time Updates",
    description: "Changes sync instantly so your team is always on the same page.",
  },
  {
    icon: Users,
    title: "Collaboration",
    description: "Invite teammates, assign tasks, and track progress together.",
  },
];
