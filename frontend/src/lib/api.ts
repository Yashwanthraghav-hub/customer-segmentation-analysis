export type RecordRow = Record<string, string | number | null>;
export type Segment = { id: string; name: string; customers: number; share: number; value: number; color: string; note?: string };
export type Overview = { customers: number; revenue: number; avgSpend: number; avgOrder: number; trend: { month: string; revenue: number }[]; segments: Segment[] };
export type AnalyzeResponse = { analytics: { kpis: { total_customers:number; total_revenue:number; average_customer_spend:number|null; average_order_value:number|null; average_purchase_frequency:number|null }; charts: Record<string,{label:string;value:number}[]> } };
export type SegmentResponse = { segmentation: { profiles: { cluster_id:number; name:string; count:number; percentage:number; averages:Record<string,number>; strategy:string }[]; points: RecordRow[] } };
const base = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '');
export const apiConfigMessage = 'Set VITE_API_BASE_URL to the Customer Segmentation API (for example http://localhost:8000) to run analysis.';
async function post<T>(path:string, records:RecordRow[]):Promise<T>{
  if(!base) throw new Error(apiConfigMessage);
  const response=await fetch(`${base}${path}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({records})});
  const json=await response.json().catch(()=>null);
  if(!response.ok) throw new Error(json?.detail || `Request failed (${response.status})`);
  return json as T;
}
export const api={ analyze:(records:RecordRow[])=>post<AnalyzeResponse>('/api/analyze',records), segment:(records:RecordRow[])=>post<SegmentResponse>('/api/segment',records), rfm:(records:RecordRow[])=>post<{distribution:{label:string;value:number}[];records:RecordRow[]}>('/api/rfm',records), insights:(records:RecordRow[])=>post<{insights:{title:string;body:string;priority:string}[];recommendations:{segment:string;opportunity:string;action:string;priority:string}[]}>('/api/insights',records) };
