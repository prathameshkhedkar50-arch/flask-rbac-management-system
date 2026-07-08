type StaticCard={
    title:string
    text:string
}

export function renderStaticPage(title:string, eyebrow:string, subtitle:string, cards:StaticCard[]){
    const el=document.getElementById("content")
    if(!el)return

    el.innerHTML=`
        <div class="page">
            <div class="page-header">
                <div>
                    <p class="eyebrow">${eyebrow}</p>
                    <h1 class="page-title">${title}</h1>
                    <p class="page-subtitle">${subtitle}</p>
                </div>
                <span class="badge">Read only</span>
            </div>

            <div class="placeholder-grid">
                ${cards.map(card=>`
                    <div class="placeholder-card">
                        <h3>${card.title}</h3>
                        <p>${card.text}</p>
                    </div>
                `).join("")}
            </div>
        </div>
    `
}
