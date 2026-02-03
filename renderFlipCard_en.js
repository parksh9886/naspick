function renderFlipCard(data) {
    return `
                <div class="flip-card-container">
                    <!-- Tab Controller -->
                    <div class="relative w-[300px] h-11 bg-[#1c1c21] rounded-full p-1 mx-auto mb-6 flex items-center shadow-inner border border-gray-800 select-none">
                        <div id="segmentSlider" class="absolute left-1 top-1 w-[146px] h-9 bg-[#2962ff] rounded-full shadow-[0_0_15px_rgba(41,98,255,0.4)] transition-all duration-300 ease-out z-0"></div>
                        <button onclick="toggleFlipCard(false)" id="tabAnalysis" class="flex-1 relative z-10 text-xs font-bold text-white text-center transition-colors h-full flex items-center justify-center active">💰 Analysis</button>
                        <button onclick="toggleFlipCard(true)" id="tabChart" class="flex-1 relative z-10 text-xs font-bold text-gray-400 text-center transition-colors h-full flex items-center justify-center">📊 Chart</button>
                    </div>

                    <!-- Content Area (Fixed Height) -->
                    <div class="relative w-full h-[540px] bg-[#131722] rounded-2xl border border-gray-800 overflow-hidden shadow-2xl">

                        <!-- View 1: Analysis (Default: Visible) -->
                        <div id="viewAnalysis" class="absolute inset-0 w-full h-full z-20 bg-[#131722] flex flex-col">
                            <!-- Gradient Header -->
                            <div class="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-[#2962ff]/10 to-transparent pointer-events-none"></div>

                            <!-- Input Content -->
                            <div class="relative z-10 flex-1 flex flex-col items-center justify-center p-8 text-center">
                                <h3 class="text-2xl font-black text-white mb-2 tracking-tight">💰 Position Analysis</h3>
                                <p class="text-gray-400 text-sm mb-10 font-medium">Enter your average price for AI diagnosis</p>
                                
                                <div class="w-full max-w-xs space-y-6">
                                    <div class="relative group">
                                        <input type="number" id="avgPriceInput" placeholder=" " 
                                            class="peer w-full bg-[#1c1c21] border border-gray-700 rounded-xl px-4 pt-6 pb-2 text-white text-xl font-bold font-mono outline-none focus:border-[#2962ff] focus:ring-1 focus:ring-[#2962ff] transition-all shadow-inner text-center">
                                        <label class="absolute text-gray-500 text-xs font-bold top-2 left-0 right-0 transition-all peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-focus:top-2 peer-focus:text-xs peer-focus:text-[#2962ff]">Average Cost ($)</label>
                                    </div>

                                    <button onclick="analyzeAvgPrice()" 
                                        class="w-full bg-gradient-to-r from-[#2962ff] to-[#0039cb] hover:from-[#448aff] hover:to-[#2962ff] text-white font-bold py-4 rounded-xl shadow-[0_10px_20px_rgba(41,98,255,0.3)] transition-all transform hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2 group">
                                        <span>Start Analysis</span>
                                        <svg class="w-5 h-5 group-hover:translate-x-1 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path></svg>
                                    </button>
                                    
                                    <p class="text-[10px] text-gray-500 text-center bg-[#1c1c21] py-2 px-3 rounded-lg border border-gray-800">
                                        * Analysis based on 4-year Volume Profile
                                    </p>
                                </div>
                            </div>

                            <!-- Result Overlay (Hidden Default) -->
                            <div id="analysisResult" class="absolute inset-0 bg-[#131722] z-30 hidden flex flex-col animate-fade-in">
                                <!-- Injected by JS -->
                            </div>
                        </div>

                        <!-- View 2: Chart (Default: Hidden) -->
                        <div id="viewChart" class="absolute inset-0 w-full h-full z-10 hidden bg-[#131722]">
                            <div id="tv_chart_container" class="w-full h-full"></div>
                        </div>
                    </div>
                </div>
            `;
}
