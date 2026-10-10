"use client";
import { useCallback, useEffect, useState } from "react";
import { eventSocketUrl, loadJobs, loadMetrics, loadWorkers } from "@/lib/api";
import type { JobView, Metrics, WorkerView } from "@/lib/types";
interface DashboardState { jobs: JobView[]; workers: WorkerView[]; metrics: Metrics | null; error: string | null; connection: "connecting" | "live" | "reconnecting"; }
export function useDashboard(): DashboardState {
 const [state,setState]=useState<DashboardState>({jobs:[],workers:[],metrics:null,error:null,connection:"connecting"});
 const refresh=useCallback(async()=>{try{const [jobPage,workers,metrics]=await Promise.all([loadJobs(),loadWorkers(),loadMetrics()]);setState((current)=>({...current,jobs:jobPage.items,workers,metrics,error:null}));}catch(error){const message=error instanceof Error?error.message:"Coordinator is unavailable";setState((current)=>({...current,error:message}));}},[]);
 useEffect(()=>{void refresh();const fallback=window.setInterval(()=>void refresh(),10_000);let socket:WebSocket|null=null;let retryTimer:number|undefined;let disposed=false;
 const connect=()=>{if(disposed)return;setState((current)=>({...current,connection:"connecting"}));socket=new WebSocket(eventSocketUrl());socket.onopen=()=>setState((current)=>({...current,connection:"live"}));socket.onmessage=()=>void refresh();socket.onclose=()=>{if(!disposed){setState((current)=>({...current,connection:"reconnecting"}));retryTimer=window.setTimeout(connect,2_000);}};socket.onerror=()=>socket?.close();};connect();return()=>{disposed=true;window.clearInterval(fallback);if(retryTimer)window.clearTimeout(retryTimer);socket?.close();};},[refresh]);return state;
}
