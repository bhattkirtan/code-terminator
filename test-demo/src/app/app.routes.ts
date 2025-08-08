import { Routes, Router } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';

const authGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  return router.parseUrl('/login');
};

export const routes: Routes = [
  { path: 'login', component: LoginComponent, data: { breadcrumb: 'Login' } },
  { path: 'dashboard', component: DashboardComponent, canActivate: [authGuard], data: { breadcrumb: 'Dashboard' } },
  { path: '', component: LandingPageComponent, data: { breadcrumb: 'Home' } },
  { path: '**', redirectTo: '' } // Redirect any unknown paths to the home page
];
