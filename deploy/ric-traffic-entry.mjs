import original from "./worker.mjs";
export * from "./worker.mjs";
import {recordRequest} from "./ric-request-telemetry.mjs";
export default {...original,async fetch(request,env,ctx){try{recordRequest(request,ctx);}catch{}return original.fetch.call(original,request,env,ctx);}};
