import { api, clearStoredUser, getStoredUser, saveStoredUser } from "./api"

export async function renderDashboard(){
    const user=getStoredUser()

    if(!user || !user.role_id){
        location.href="/login"
        return
    }

    let menus:any[]=[]
    try{
        menus=await api("/my-menus")
    }catch{
        clearStoredUser()
        location.href="/login"
        return
    }
    user.menus=menus.map((m:any)=>m.name.toLowerCase())
    saveStoredUser(user)

    const currentPath=location.pathname==="/" ? "dashboard" : location.pathname.replace("/","")
    const isDashboard=currentPath==="dashboard"

    function iconLabel(name:string){
        return name.slice(0,2).toUpperCase()
    }

    document.body.innerHTML=`
    <div class="app-shell">
        <aside class="sidebar">
            <div class="sidebar-brand">
                <div class="brand-mark">RB</div>
                <div>
                    <div class="brand-title">RBAC Admin</div>
                    <div class="brand-subtitle">Operations Console</div>
                </div>
            </div>

            <ul class="sidebar-nav">
                ${menus.map((m:any)=>`
                    <li onclick="go('/${m.name.toLowerCase()}')"
                        class="sidebar-item ${currentPath===m.name.toLowerCase() ? "active" : ""}">
                        <span class="sidebar-icon">${iconLabel(m.name)}</span>
                        <span>${m.name}</span>
                    </li>
                `).join("")}
            </ul>

            <div class="sidebar-footer">
                <div class="user-chip">
                    <strong>${user.user||"User"}</strong>
                    <span>${user.role_name||"Logged in"}</span>
                </div>
                <button id="logout" class="btn btn-ghost">Logout</button>
            </div>
        </aside>

        <main id="content" class="main-content">
            <div class="page">
                <div class="page-header">
                    <div>
                        <p class="eyebrow">Dashboard</p>
                        <h1 class="page-title">Business Overview</h1>
                        <p class="page-subtitle">Welcome ${user.user||"User"}. Your accessible modules are ready.</p>
                    </div>
                </div>
                ${isDashboard ? `<div id="dashboardCards" class="dashboard-grid"><div class="loading">Loading dashboard totals...</div></div>` : ""}
            </div>
        </main>

    </div>
    `

    document.getElementById("logout")!.onclick=()=>{
        clearStoredUser()
        location.href="/login"
    }

    if(isDashboard){
        const cards=document.getElementById("dashboardCards")

        if(cards){
            try{
                const stats=await api("/dashboard-stats")
                const items=[
                    ["US","Total Users",stats.users],
                    ["PR","Total Products",stats.products],
                    ["OR","Total Orders",stats.orders],
                    ["CU","Total Customers",stats.customers],
                    ["SU","Total Suppliers",stats.suppliers]
                ]

                cards.innerHTML=items.map(([icon,label,value])=>`
                    <div class="stat-card">
                        <div class="stat-icon">${icon}</div>
                        <div class="stat-label">${label}</div>
                        <div class="stat-value">${value}</div>
                    </div>
                `).join("") + `
                    <div class="panel panel-body">
                        <div class="toolbar">
                            <div>
                                <h2 class="section-title">Quick Actions</h2>
                                <p class="page-subtitle">Jump to frequently used modules available to your role.</p>
                            </div>
                        </div>
                        <div class="quick-actions">
                            ${menus
                                .filter((m:any)=>["Users","Orders","Products","Customers","Suppliers","Admin"].includes(m.name))
                                .map((m:any)=>`
                                    <button class="btn quick-action" onclick="go('/${m.name.toLowerCase()}')">
                                        <span class="sidebar-icon">${iconLabel(m.name)}</span>
                                        ${m.name}
                                    </button>
                                `).join("")}
                        </div>
                    </div>
                `
            }catch{
                cards.innerHTML=`<p class="message error">Unable to load dashboard totals</p>`
            }
        }
    }
}
