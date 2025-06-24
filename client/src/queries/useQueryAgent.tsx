import { useMutation } from "react-query";
import { DefaultService } from "../fastapi_client/services/DefaultService";
import type {
  AgentRequestOptions,
  EndpointRequestOptions,
  LogAssessmentRequestOptions,
  QueryAgentResponse,
} from "@/fastapi_client";
export interface AgentResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: {
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
    logprobs: any;
  }[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export function useQueryAgent() {
  return useMutation({
    mutationFn: async (
      request: AgentRequestOptions,
    ): Promise<{ response: AgentResponse } & QueryAgentResponse> => {
      return DefaultService.agentApiAgentPost(request);
    },
  });
}

export function useModelServing() {
  return useMutation({
    mutationFn: async (
      request: EndpointRequestOptions,
    ): Promise<AgentResponse> => {
      return DefaultService.invokeEndpointApiInvokeEndpointPost(request);
    },
  });
}

export function useLogFeedback() {
  return useMutation({
    mutationFn: async (request: LogAssessmentRequestOptions) => {
      return DefaultService.logFeedbackApiLogAssessmentPost(request);
    },
  });
}
