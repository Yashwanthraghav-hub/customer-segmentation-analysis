import { useSyncExternalStore } from 'react';
import type { RecordRow } from './api';
let records: RecordRow[]=[]; let listeners:(()=>void)[]=[];
const emit=()=>listeners.forEach(listener=>listener());
export function setRecords(next:RecordRow[]){records=next;emit()}
export function useDataset(){return useSyncExternalStore((listener)=>{listeners=[...listeners,listener];return()=>{listeners=listeners.filter(x=>x!==listener)}},()=>records,()=>records)}
export function parseCsv(text:string):RecordRow[]{const [head,...lines]=text.trim().split(/\r?\n/);const headers=head.split(',');return lines.filter(Boolean).map(line=>{const values=line.split(',');return Object.fromEntries(headers.map((header,i)=>{const raw=values[i]?.trim()??'';return [header,raw!==''&&!Number.isNaN(Number(raw))?Number(raw):raw]}))})}
export async function loadSample(){const response=await fetch('/sample_customers.csv');if(!response.ok)throw new Error('The bundled sample dataset could not be loaded.');const rows=parseCsv(await response.text());setRecords(rows);return rows}
