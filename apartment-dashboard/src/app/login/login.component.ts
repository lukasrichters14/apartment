import { Component, OnInit } from '@angular/core';
import {FormControl, FormGroup} from "@angular/forms";
import {ApiService} from "../api.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  // Error displays.
  required = false;
  errMessage: string = '';

  // Forms.
  residentGroup = new FormGroup({
    name : new FormControl(''),
    email : new FormControl('')
  })

  constructor(private api: ApiService, private router:Router) { }

  ngOnInit(): void {
  }

  /**
   * Submits the form to the proper API endpoint based on which page submitted the form.
   */
  onSubmit(): void {
    // First stage of login as a resident, submit info in order to get a code sent by email.
    // Display required error.
    if (this.residentGroup.value['name'] == '' || this.residentGroup.value['email'] == '') {
      this.required = true;
      return
    }
    // Turn off required error.
    this.required = false;
    // First stage of login requires name and email.
    this.api.login(this.residentGroup.value['name'], this.residentGroup.value['email'])
      .subscribe(resp => {
        // Display the error message from the API if one occurs.
        if (resp.hasOwnProperty('error')) {
          this.errMessage = resp['error'];
        }
        // Navigate user to the login code page, since they had valid credentials.
        else {
          // Remove any error message.
          this.errMessage = '';
          this.router.navigateByUrl('login/code')
        }
      });
  }

}
