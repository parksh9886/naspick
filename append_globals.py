
import os

LOGIC_FILE = r'c:\Users\sec\Desktop\Naspick\restored_logic.js'

GLOBAL_FUNCS = """

// --- Global Event Handlers ---

function toggleFlipCard(showBack) {
    const card = document.getElementById('flipCard');
    const slider = document.getElementById('segmentSlider');
    const tabChart = document.getElementById('tabChart');
    const tabAnalysis = document.getElementById('tabAnalysis');
    
    if (showBack) {
        card.classList.add('flipped');
        slider.style.transform = 'translateX(100%)';
        tabChart.classList.remove('active');
        tabAnalysis.classList.add('active');
    } else {
        card.classList.remove('flipped');
        slider.style.transform = 'translateX(0)';
        tabChart.classList.add('active');
        tabAnalysis.classList.remove('active');
    }
}

function switchRelatedTab(type) {
    const sectorList = document.getElementById('sectorLeaderList');
    const similarList = document.getElementById('similarScoreList');
    const tabSector = document.getElementById('tabSectorLeader');
    const tabSimilar = document.getElementById('tabSimilarScore');

    if (!sectorList || !similarList) return;

    if (type === 'sector') {
        sectorList.classList.remove('hidden');
        similarList.classList.add('hidden');
        
        tabSector.classList.remove('text-gray-400', 'hover:text-gray-200');
        tabSector.classList.add('bg-[#5383e8]', 'text-white');
        
        tabSimilar.classList.remove('bg-[#5383e8]', 'text-white');
        tabSimilar.classList.add('text-gray-400', 'hover:text-gray-200');
    } else {
        sectorList.classList.add('hidden');
        similarList.classList.remove('hidden');
        
        tabSimilar.classList.remove('text-gray-400', 'hover:text-gray-200');
        tabSimilar.classList.add('bg-[#5383e8]', 'text-white');
        
        tabSector.classList.remove('bg-[#5383e8]', 'text-white');
        tabSector.classList.add('text-gray-400', 'hover:text-gray-200');
    }
}

function analyzeAvgPrice() {
    const avgInput = document.getElementById('avgPriceInput');
    const qtyInput = document.getElementById('quantityInput');
    const resultDiv = document.getElementById('analysisResult');
    
    if (!avgInput || !qtyInput || !resultDiv) return;

    const avgPrice = parseFloat(avgInput.value);
    const quantity = parseFloat(qtyInput.value);

    if (!avgPrice || avgPrice <= 0) {
        alert('유효한 매수가를 입력해주세요.'); 
        return;
    }

    // Try global var first, then DOM fallback
    let cp = window.currentStockPrice;
    if (!cp) {
         const priceEl = document.querySelector('.text-4xl'); // Desktop price
         if(priceEl) {
             const txt = priceEl.textContent.replace('$','').replace(',','');
             cp = parseFloat(txt);
         }
    }
    
    if (!cp) {
        resultDiv.innerHTML = '<div class="text-red-400 text-center">현재가 정보를 불러올 수 없습니다.</div>';
        resultDiv.classList.remove('hidden');
        return;
    }

    const pnlPercent = ((cp - avgPrice) / avgPrice * 100).toFixed(2);
    const pnlAmount = quantity ? ((cp - avgPrice) * quantity).toFixed(2) : null;
    const isProfit = pnlPercent >= 0;
    const color = isProfit ? 'text-green-400' : 'text-red-400';
    const sign = isProfit ? '+' : '';

    resultDiv.innerHTML = `
        <div class="text-center">
             <div class="text-gray-400 text-xs mb-1">현재가 $${cp} / 평단가 $${avgPrice}</div>
             <div class="text-3xl font-bold ${color} mb-1">${sign}${pnlPercent}%</div>
             ${pnlAmount ? `<div class="text-lg ${color} font-bold">${sign}$${pnlAmount}</div>` : ''}
        </div>
    `;
    resultDiv.classList.remove('hidden');
}
"""

if __name__ == "__main__":
    if not os.path.exists(LOGIC_FILE):
        print(f"Error: {LOGIC_FILE} not found")
    else:
        with open(LOGIC_FILE, 'a', encoding='utf-8') as f:
            f.write(GLOBAL_FUNCS)
        print(f"Successfully appended global functions to {LOGIC_FILE}")
