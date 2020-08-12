import { Component, OnInit } from '@angular/core';
import {FormControl, FormGroup, Validators} from "@angular/forms";
import {ApiService} from "../api.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  // Error displays.
  required = false;
  errMessage: string = '';

  registerGroup = new FormGroup({
    word1 : new FormControl('', Validators.required),
    word2 : new FormControl('', Validators.required),
    word3 : new FormControl('', Validators.required),
    word4 : new FormControl('', Validators.required),
    word5 : new FormControl('', Validators.required),
    name : new FormControl('', Validators.required),
    email : new FormControl('', Validators.required)
  })

  constructor(private api: ApiService, private router: Router) { }

  ngOnInit(): void {
  }

  onSubmit(): void {
    // Display required error.
    if (this.registerGroup.invalid){
      this.required = true;
      return
    }
    // Turn off required error.
    this.required = false;

    // Concatenate registration code.
    let registrationCode = `${this.registerGroup.value['word1']}-${this.registerGroup.value['word2']}-${this.registerGroup.value['word3']}-${this.registerGroup.value['word4']}-${this.registerGroup.value['word5']}`

    this.api.register(registrationCode, this.registerGroup.value['name'], this.registerGroup.value['email'])
      .subscribe(resp => {
        // If the cookie is returned from the API, the code will view that as a null value.
        if(resp != null){
          // Display the error message from the API if one occurs.
          if (resp.hasOwnProperty('error')){
            this.errMessage = resp['error'];
          }
        }
        // No error, navigate to the menu.
        else{
          // Remove any error message.
          this.errMessage = '';
          this.router.navigateByUrl('menu')
        }
      });
  }

}
