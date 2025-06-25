import "./index.css"; // Tailwind styles
import React, { use, useEffect } from "react";
import "./App.css";
import { QueryClient, QueryClientProvider } from "react-query";
import {
  useLogFeedback,
  useModelServing,
  useQueryAgent as useQueryCustomAgent,
} from "@/queries/useQueryAgent";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Plus, ArrowUp } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ENDPOINTS } from "@/endpoints";
import { useQueryExperiment } from "@/queries/useQueryTracing";
import { Spinner } from "@/components/Spinner";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { MessageContent } from "@/components/MessageContent";

const queryClient = new QueryClient();

export function Chat() {
  const [messages, setMessages] = useState<
    {
      role: "user" | "system" | "assistant";
      content: string;
      traceId?: string;
    }[]
  >([]);
  const [input, setInput] = useState("");
  const lastMessageRef = React.useRef<HTMLDivElement>(null);

  const { data: experiment, isLoading: experimentIsLoading } =
    useQueryExperiment();

  const {
    mutate: mutateCustom,
    isLoading: isCustomLoading,
    isError: isCustomError,
    error,
    data,
  } = useQueryCustomAgent();
  const {
    mutate: mutateModelServing,
    isLoading: isModelServingLoading,
    isError: isModelServingError,
    error: modelServingError,
    data: modelServingData,
  } = useModelServing();

  const sendMessage = async () => {
    if (!input.trim() || isCustomLoading) return;

    const userMessage: { role: "user"; content: string } = {
      role: "user",
      content: input,
    };
    setMessages([...messages, userMessage]);
    const endpoint = ENDPOINTS.find(
      (endpoint) => endpoint.endpointName === selectedAgent,
    );

    if (endpoint != null) {
      mutateModelServing(
        {
          endpoint_name: endpoint.endpointName,
          messages: [...messages, { role: "user", content: input }],
        },
        {
          onSuccess: (data) => {
            const responseMessage = data?.choices[0].message;
            setMessages((prev) => [
              ...prev,
              {
                traceId: "",
                role: "assistant",
                content: responseMessage.content,
              },
            ]);
          },
        },
      );
      setInput("");
      return;
    } else {
      mutateCustom(
        {
          inputs: { messages: [...messages, { role: "user", content: input }] },
        },
        {
          onSuccess: (data) => {
            const responseMessage = data?.response.choices[0].message;
            setMessages((prev) => [
              ...prev,
              {
                traceId: data?.trace_id || undefined,
                role: "assistant",
                content: responseMessage.content,
              },
            ]);
          },
        },
      );
    }

    setInput("");
  };

  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const isLoading = isCustomLoading || isModelServingLoading;
  const isError = isCustomError || isModelServingError;

  const [selectedAgent, setSelectedAgent] = useState("default");

  return (
    <TooltipProvider>
      <SidebarProvider>
        <AppSidebar 
          selectedAgent={selectedAgent}
          setSelectedAgent={setSelectedAgent}
          setMessages={setMessages}
          experiment={experiment}
          experimentIsLoading={experimentIsLoading}
        />
        <main className="flex-1 flex items-center justify-center p-4">
          <Card className="flex flex-col w-full max-w-md shadow-sm h-[600px]">
          <CardHeader className="flex flex-row items-center">
            <div className="flex items-center gap-4">
              <Avatar className="size-8 border">
                <AvatarImage src="/avatars/assistant.png" alt="Assistant" />
                <AvatarFallback>AI</AvatarFallback>
              </Avatar>
              <div className="flex flex-col gap-0.5">
                <p className="text-sm font-medium leading-none">Databricks Agent</p>
                <p className="text-xs text-muted-foreground">Ready to help</p>
              </div>
            </div>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="secondary"
                  size="icon"
                  className="ml-auto size-8 rounded-full"
                  onClick={() => setMessages([])}
                >
                  <Plus className="size-4" />
                  <span className="sr-only">New conversation</span>
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>New conversation</p>
              </TooltipContent>
            </Tooltip>
          </CardHeader>

          <CardContent className="flex-1 overflow-hidden">
            <ScrollArea className="h-full w-full">
              <div className="flex flex-col gap-4 p-1 min-h-full">
                <div className="flex w-fit max-w-[75%] flex-col gap-2 rounded-lg px-3 py-2 text-sm bg-muted">
                  <MessageContent content="Hi, how can I help you today?" />
                </div>
                {messages.map((msg, i) => (
                  <div key={i} className="flex flex-col gap-2">
                    <div
                      ref={i === messages.length - 1 ? lastMessageRef : null}
                      className={`flex w-fit max-w-[75%] flex-col gap-2 rounded-lg px-3 py-2 text-sm ${
                        msg.role === "user"
                          ? "bg-primary text-primary-foreground ml-auto"
                          : "bg-muted"
                      }`}
                    >
                      <MessageContent content={msg.content} />
                    </div>
                    {msg.role === "assistant" && (
                      <div className="flex justify-start">
                        <Feedback traceId={msg.traceId || ""} />
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div
                    ref={lastMessageRef}
                    className="flex w-fit max-w-[75%] flex-col gap-2 rounded-lg px-3 py-2 text-sm bg-muted"
                  >
                    <span className="italic">Typing...</span>
                  </div>
                )}
              </div>
            </ScrollArea>
          </CardContent>

          {isError && (
            <div className="px-6 pb-2">
              <p className="text-red-500 text-sm">{isError}</p>
            </div>
          )}

          <CardFooter className="flex items-center">
            <form
              className="relative w-full"
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
            >
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 pr-10"
                autoComplete="off"
              />
              <Button
                type="submit"
                size="icon"
                className="absolute top-1/2 right-2 size-6 -translate-y-1/2 rounded-full"
                disabled={isLoading || !input.trim()}
              >
                <ArrowUp className="size-3.5" />
                <span className="sr-only">Send</span>
              </Button>
            </form>
          </CardFooter>
        </Card>
        </main>
      </SidebarProvider>
    </TooltipProvider>
  );
}

export const Feedback = ({ traceId }: { traceId: string }) => {
  const { mutate: logFeedback, isLoading: isFeedbackLoading } =
    useLogFeedback();
  const [feedback, setFeedback] = useState<boolean | null>(null);
  const [pendingFeedback, setPendingFeedback] = useState<boolean | null>(null);

  const handleFeedback = (value: boolean) => {
    setPendingFeedback(value);
    logFeedback(
      {
        trace_id: traceId,
        assessment_name: "good_response0",
        assessment_value: value,
      },
      {
        onSuccess: () => {
          setFeedback(value);
          setPendingFeedback(null);
        },
        onError: () => {
          setPendingFeedback(null);
        },
      },
    );
  };

  return (
    <div className="flex gap-1">
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleFeedback(true)}
        disabled={feedback !== null || isFeedbackLoading}
        className={`h-8 w-8 p-0 ${
          feedback === true
            ? "bg-green-50 border-green-200 text-green-700 hover:bg-green-50"
            : pendingFeedback === true && isFeedbackLoading
              ? "bg-blue-50 border-blue-200"
              : ""
        }`}
      >
        {pendingFeedback === true && isFeedbackLoading ? (
          <div className="animate-spin h-3 w-3 border border-blue-500 border-t-transparent rounded-full" />
        ) : (
          "👍"
        )}
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleFeedback(false)}
        disabled={feedback !== null || isFeedbackLoading}
        className={`h-8 w-8 p-0 ${
          feedback === false
            ? "bg-red-50 border-red-200 text-red-700 hover:bg-red-50"
            : pendingFeedback === false && isFeedbackLoading
              ? "bg-blue-50 border-blue-200"
              : ""
        }`}
      >
        {pendingFeedback === false && isFeedbackLoading ? (
          <div className="animate-spin h-3 w-3 border border-blue-500 border-t-transparent rounded-full" />
        ) : (
          "👎"
        )}
      </Button>
    </div>
  );
};

function App() {
  return (
    <>
      <QueryClientProvider client={queryClient}>
        <Chat />
      </QueryClientProvider>
    </>
  );
}

export default App;
