const V="upnivo-v4",SHELL=["/","/static/logo.png","/static/icon-192.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener("message",e=>{if(e.data&&e.data.type==="SKIP")self.skipWaiting()});
self.addEventListener("fetch",e=>{const r=e.request,u=new URL(r.url);if(r.method!=="GET"||u.origin!==location.origin||u.pathname.startsWith("/api/"))return;
 const fast=u.pathname.startsWith("/static/covers")||u.pathname.startsWith("/uploads")||/\.(png|svg|jpg|webp)$/.test(u.pathname);
 if(fast){e.respondWith(caches.match(r).then(m=>m||fetch(r).then(x=>{if(x.ok){const c=x.clone();caches.open(V).then(h=>h.put(r,c))}return x})));return}
 e.respondWith(fetch(r).then(x=>{if(x.ok){const c=x.clone();caches.open(V).then(h=>h.put(r,c))}return x}).catch(()=>caches.match(r).then(m=>m||caches.match("/"))))});
self.addEventListener("push",e=>{let d={};try{d=e.data.json()}catch(x){d={title:"UPNIVO INTERN",body:e.data?e.data.text():""}}
 e.waitUntil(self.registration.showNotification(d.title||"UPNIVO INTERN",{body:d.body||"",icon:"/static/icon-192.png",badge:"/static/icon-192.png",data:{link:d.link||""},vibrate:[120,60,120]}))});
self.addEventListener("notificationclick",e=>{e.notification.close();const l=(e.notification.data&&e.notification.data.link)||"";
 e.waitUntil(clients.matchAll({type:"window",includeUncontrolled:true}).then(w=>{const url="/"+(l?"#"+l:"");for(const c of w){if("focus"in c){c.navigate&&c.navigate(url);return c.focus()}}return clients.openWindow(url)}))});
