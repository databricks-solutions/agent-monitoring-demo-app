"use client"

import * as React from "react"
import {
  Settings,
  Bot,
  Database,
  Link,
} from "lucide-react"

import { NavDocuments } from "@/components/nav-documents"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const data = {
  user: {
    name: "Developer",
    email: "dev@databricks.com",
    avatar: "/avatars/assistant.png",
  },
  navSecondary: [
    {
      title: "Settings", 
      url: "#",
      icon: Settings,
    },
  ],
  documents: [
    {
      name: "Agent Configuration",
      url: "#",
      icon: Bot,
    },
    {
      name: "MLFlow Experiment",
      url: "#", 
      icon: Database,
    },
    {
      name: "API Endpoints",
      url: "#",
      icon: Link,
    },
  ],
}

export function AppSidebar({ 
  children,
  selectedAgent,
  setSelectedAgent,
  setMessages,
  experiment,
  experimentIsLoading,
  ...props 
}: React.ComponentProps<typeof Sidebar> & {
  children?: React.ReactNode
  selectedAgent: string
  setSelectedAgent: (value: string) => void
  setMessages: (value: any) => void
  experiment: any
  experimentIsLoading: boolean
}) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild size="lg">
              <a href="#">
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Bot className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">Databricks Agent</span>
                  <span className="truncate text-xs">AI Assistant</span>
                </div>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        {children}
        <NavDocuments 
          selectedAgent={selectedAgent}
          setSelectedAgent={setSelectedAgent}
          setMessages={setMessages}
          experiment={experiment}
          experimentIsLoading={experimentIsLoading}
        />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}