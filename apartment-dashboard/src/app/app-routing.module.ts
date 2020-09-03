import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {MenuComponent} from "./menu/menu.component";
import {LoginComponent} from "./login/login.component";
import {RegisterComponent} from "./register/register.component";
import {LoginGuestComponent} from "./login-guest/login-guest.component";
import {LoginCodeComponent} from "./login-code/login-code.component";
import {DashboardComponent} from "./dashboard/dashboard.component";
import {SpotifyComponent} from "./spotify/spotify.component";


const routes: Routes = [
  {path: '', redirectTo: 'login', pathMatch: 'full'},
  {path: 'login', component: LoginComponent},
  {path: 'login/code', component: LoginCodeComponent},
  {path: 'register', component: RegisterComponent},
  {path: 'login-guest', component: LoginGuestComponent},
  {path: 'menu', component: MenuComponent},
  {path: 'dashboard', component: DashboardComponent},
  {path: 'spotify', component: SpotifyComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
