"use client"

import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ENDPOINTS } from "@/endpoints"
import { Spinner } from "@/components/Spinner"

export function NavDocuments({
  selectedAgent,
  setSelectedAgent,
  setMessages,
  experiment,
  experimentIsLoading,
}: {
  selectedAgent: string
  setSelectedAgent: (value: string) => void
  setMessages: (value: any) => void
  experiment: any
  experimentIsLoading: boolean
}) {
  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Configuration</SidebarGroupLabel>
      <SidebarGroupContent className="space-y-4 px-2">
        <div className="space-y-2">
          <label className="text-xs font-medium text-sidebar-foreground/70">
            Select Agent
          </label>
          <Select
            onValueChange={(value) => {
              setMessages([]);
              setSelectedAgent(value);
            }}
            value={selectedAgent}
          >
            <SelectTrigger className="h-8 text-xs">
              <SelectValue placeholder="Choose an agent" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="default">Custom system prompt</SelectItem>
              {ENDPOINTS.map((endpoint) => (
                <SelectItem
                  key={endpoint.endpointName}
                  value={endpoint.endpointName}
                >
                  {endpoint.displayName}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <label className="text-xs font-medium text-sidebar-foreground/70">
            MLFlow Experiment ID
          </label>
          <div className="text-xs">
            {experimentIsLoading && <Spinner size={4} />}
            {!experimentIsLoading && (
              <a
                href={experiment?.["link"]}
                className="text-blue-500 hover:underline break-all"
                target="_blank"
                rel="noopener noreferrer"
              >
                {experiment?.["experiment_id"]}
              </a>
            )}
          </div>
        </div>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}