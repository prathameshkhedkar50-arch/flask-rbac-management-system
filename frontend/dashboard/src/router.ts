import { api, clearStoredUser, getStoredUser, saveStoredUser } from "./api"

export function go(path:string){
    const cleanPath=(path.startsWith("/") ? path : `/${path}`).toLowerCase()
    history.pushState({},'',cleanPath)
    render()
}

window.onpopstate=()=>render()

export async function render(){
    const path=(location.pathname || "/").toLowerCase()
    let user=getStoredUser()

    if(!user || !user.role_id){
        if(path!=="/login"){
            history.replaceState({},'',"/login")
        }
        return import("./login").then(m=>m.renderLogin())
    }

    if(path==="/login"){
        history.replaceState({},'',"/")
        return import("./dashboard").then(m=>m.renderDashboard())
    }

    if(!user.menus){
        try{
            const menus=await api("/my-menus")
            user.menus=menus.map((m:any)=>m.name.toLowerCase())
            saveStoredUser(user)
        }catch{
            clearStoredUser()
            location.href="/login"
            return
        }
    }

    if(!document.getElementById("content")){
        await import("./dashboard").then(m=>m.renderDashboard())
    }

    function block(){
        document.getElementById("content")!.innerHTML=`
            <div class="page">
                <div class="access-denied">
                    <h2>Access Denied</h2>
                    <p>You do not have permission to open this module.</p>
                </div>
            </div>
        `
    }

    const routes:any={
        "/":{module:"dashboard",loader:()=>import("./dashboard").then(m=>m.renderDashboard())},
        "/dashboard":{module:"dashboard",loader:()=>import("./dashboard").then(m=>m.renderDashboard())},
        "/users":{module:"users",loader:()=>import("./pages/users").then(m=>m.renderUsers())},
        "/orders":{module:"orders",loader:()=>import("./pages/orders").then(m=>m.renderOrders())},
        "/reports":{module:"reports",loader:()=>import("./pages/reports").then(m=>m.renderReports())},
        "/products":{module:"products",loader:()=>import("./pages/products").then(m=>m.renderProducts())},
        "/settings":{module:"settings",loader:()=>import("./pages/settings").then(m=>m.renderSettings())},
        "/invoices":{module:"invoices",loader:()=>import("./pages/invoices").then(m=>m.renderInvoices())},
        "/customers":{module:"customers",loader:()=>import("./pages/customers").then(m=>m.renderCustomers())},
        "/suppliers":{module:"suppliers",loader:()=>import("./pages/suppliers").then(m=>m.renderSuppliers())},
        "/analytics":{module:"analytics",loader:()=>import("./pages/analytics").then(m=>m.renderAnalytics())},
        "/admin":{module:"admin",admin:true,loader:()=>import("./pages/admin").then(m=>m.renderAdmin())}
    }

    const route=routes[path] || routes["/dashboard"]

    if(!user.menus.includes(route.module)) return block()
    if(route.admin && user.role_name!=="Admin" && user.role_id!==1) return block()

    return route.loader()
}

(window as any).go=go
