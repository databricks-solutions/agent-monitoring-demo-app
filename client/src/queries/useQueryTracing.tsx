import { useQuery } from "react-query";
import { DefaultService } from "../fastapi_client/services/DefaultService";

export function useQueryExperiment() {
  return useQuery({
    queryKey: ["experiment"],
    queryFn: async () => {
      return DefaultService.experimentApiTracingExperimentGet();
    },
  });
}
