import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ActivatedRoute } from '@angular/router';

import { StudentProfileService } from '../../services/student-profile.service';

@Component({
  selector: 'app-student-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './student-profile.component.html',
  styleUrl: './student-profile.component.scss'
})
export class StudentProfileComponent implements OnInit {

  private route = inject(ActivatedRoute);

  private profileService = inject(StudentProfileService);

  student: any = null;

  ngOnInit(): void {

    const id = Number(
      this.route.snapshot.paramMap.get('id')
    );

    this.profileService
      .getStudent(id)
      .subscribe({

        next: (response: any) => {

          console.log('STUDENT PROFILE', response);

          this.student = response;

        },

        error: (error) => {

          console.error(error);

        }

      });

  }

}