import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import {
  Router,
  RouterOutlet,
  RouterLink
} from '@angular/router';

@Component({
  selector: 'app-dashboard-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink
  ],
  templateUrl: './dashboard-layout.component.html',
  styleUrl: './dashboard-layout.component.scss'
})

export class DashboardLayoutComponent {

  user = JSON.parse(localStorage.getItem('user') || '{}');

  menuItems: any[] = [];

  constructor(private router: Router) {

    this.loadMenuByRole();

  }

  loadMenuByRole() {

    const role = this.user?.role?.toUpperCase();

    if (role.includes('ADMIN')) {

      this.menuItems = [

        {
          label: 'Inicio',
          icon: '🏠',
          route: '/dashboard'
        },

        {
          label: 'Estudiantes',
          icon: '👨‍🎓',
          route: '/students'
        },

        {
          label: 'Diagnósticos',
          icon: '🧠',
          route: '/diagnostics'
        },

        {
          label: 'Evaluaciones',
          icon: '📋',
          route: '/evaluations'
        }

      ];

    }

  }

  logout() {

    localStorage.clear();

    this.router.navigate(['/login']);

  }

}