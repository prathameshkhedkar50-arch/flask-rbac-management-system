import { escapeHtml } from "./api"

type ToastType = "success" | "error" | "info"

export function ensureToastRoot(){
    let root=document.getElementById("toastRoot")

    if(!root){
        root=document.createElement("div")
        root.id="toastRoot"
        root.className="toast-root"
        document.body.appendChild(root)
    }

    return root
}

export function showToast(message:string,type:ToastType="info"){
    const root=ensureToastRoot()
    const toast=document.createElement("div")
    toast.className=`toast toast-${type}`
    toast.innerHTML=escapeHtml(message)
    root.appendChild(toast)

    window.setTimeout(()=>{
        toast.classList.add("leaving")
        window.setTimeout(()=>toast.remove(),180)
    },3200)
}

export function pageLoading(title:string,subtitle:string){
    return `
        <div class="page">
            <div class="page-header">
                <div>
                    <p class="eyebrow">Loading</p>
                    <h1 class="page-title">${escapeHtml(title)}</h1>
                    <p class="page-subtitle">${escapeHtml(subtitle)}</p>
                </div>
            </div>
            <div class="panel"><div class="loading"><span class="spinner"></span> Loading data...</div></div>
        </div>
    `
}

export function emptyState(title:string,text:string){
    return `
        <div class="empty-state">
            <p class="empty-title">${escapeHtml(title)}</p>
            <p class="empty-text">${escapeHtml(text)}</p>
        </div>
    `
}

export function setBusy(button:HTMLButtonElement | null,busy:boolean,label?:string){
    if(!button)return

    if(busy){
        button.dataset.originalText=button.innerHTML
        button.disabled=true
        button.innerHTML=`<span class="spinner tiny"></span>${escapeHtml(label || "Working...")}`
        return
    }

    button.disabled=false
    if(button.dataset.originalText){
        button.innerHTML=button.dataset.originalText
        delete button.dataset.originalText
    }
}

export function confirmDialog(title:string,message:string,confirmText="Delete"){
    return new Promise<boolean>((resolve)=>{
        const overlay=document.createElement("div")
        overlay.className="modal-backdrop"
        overlay.innerHTML=`
            <div class="modal" role="dialog" aria-modal="true">
                <div class="modal-header">
                    <h2>${escapeHtml(title)}</h2>
                </div>
                <p class="modal-text">${escapeHtml(message)}</p>
                <div class="modal-actions">
                    <button id="confirmCancel" class="btn btn-secondary" type="button">Cancel</button>
                    <button id="confirmOk" class="btn btn-danger" type="button">${escapeHtml(confirmText)}</button>
                </div>
            </div>
        `

        function finish(value:boolean){
            overlay.remove()
            resolve(value)
        }

        overlay.addEventListener("click",(event)=>{
            if(event.target===overlay)finish(false)
        })

        document.body.appendChild(overlay)
        document.getElementById("confirmCancel")?.addEventListener("click",()=>finish(false))
        document.getElementById("confirmOk")?.addEventListener("click",()=>finish(true))
        document.getElementById("confirmCancel")?.focus()
    })
}
