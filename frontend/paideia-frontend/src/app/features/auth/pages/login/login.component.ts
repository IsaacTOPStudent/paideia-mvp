import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})

export class LoginComponent {

  email: string = '';
  password: string = '';

  mostrarPassword: boolean = false;

  private authService = inject(AuthService);
  private router = inject(Router);

  iniciarSesion() {

    if (!this.email || !this.password) {

      alert('Completa todos los campos');
      return;

    }

    this.authService.login(this.email, this.password)
      .subscribe({

        next: (response) => {

          console.log('LOGIN EXITOSO', response);
          console.log('USER', response.user);
          console.log('ROLE', response.user.role);
          console.log('STATUS', response.user.status);

          localStorage.setItem('access', response.access);
          localStorage.setItem('refresh', response.refresh);

          localStorage.setItem('user', JSON.stringify(response.user));

          console.log('NAVEGANDO...');

          this.router.navigateByUrl('/dashboard');

        },

        error: (error) => {

          console.error('ERROR LOGIN', error);

          alert('Credenciales incorrectas');

        }

      });

  }

}