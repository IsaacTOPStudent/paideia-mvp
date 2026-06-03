import { Routes } from '@angular/router';

import { LoginComponent } from './features/auth/pages/login/login.component';

import { DashboardLayoutComponent } from './core/layout/dashboard-layout/dashboard-layout.component';

import { DashboardComponent } from './features/dashboard/pages/dashboard/dashboard.component';

import { StudentsListComponent } from './features/students/pages/students-list/students-list.component';

import { StudentCreateComponent } from './features/students/pages/student-create/student-create.component';

import { authGuard } from './core/auth/guards/auth.guard';

import { StudentProfileComponent } from './features/students/pages/student-profile/student-profile.component';

export const routes: Routes = [

  // LOGIN
  {
    path: 'login',
    component: LoginComponent
  },

  // APP PROTEGIDA
  {
    path: '',
    component: DashboardLayoutComponent,
    canActivate: [authGuard],

    children: [

      // REDIRECT INTERNO
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },

      // DASHBOARD
      {
        path: 'dashboard',
        component: DashboardComponent
      },

      // STUDENTS
      {
        path: 'students',
        component: StudentsListComponent
      },

      // CREATE STUDENT
      {
        path: 'students/create',
        component: StudentCreateComponent
      },
      {
        path: 'students/:id',
        component: StudentProfileComponent
      }

    ]

  }

];