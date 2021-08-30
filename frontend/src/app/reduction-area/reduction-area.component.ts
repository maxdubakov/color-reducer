import {Component, ElementRef, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {ColorEvent} from "ngx-color";
import {HttpClient, HttpParams} from "@angular/common/http";
import {DomSanitizer} from "@angular/platform-browser";

// import * as fileSaver from 'file-saver';

@Component({
  selector: 'app-reduction-area',
  templateUrl: './reduction-area.component.html',
  styleUrls: ['./reduction-area.component.css']
})
export class ReductionAreaComponent implements OnInit, OnDestroy {

  @ViewChild("fileDropRef", {static: false}) fileDropEl: ElementRef | undefined;
  @ViewChild('chromeComponent') chromeComponent: any;
  @ViewChild('colorInp') colorInp: ElementRef | undefined;

  server = 'http://localhost:8000';

  currentColor: string = '#ffffff';
  handMode: boolean | undefined;
  contour: boolean | undefined;
  amountOfColors: number | undefined;
  uploaded: boolean | undefined;
  converting: boolean | undefined;
  url: any;
  convertedUrl: any;
  downloadUrl: any;

  selectedColors: string[] = [];
  file: any;
  file_uploading_sub: any;


  constructor(private http: HttpClient, private dom: DomSanitizer) {
  }

  setDefault() {
    this.currentColor = '#fff';
    this.handMode = false;
    this.contour = false;
    this.amountOfColors = 32;
    this.uploaded = false;
    this.converting = false;
    this.url = undefined;
    this.convertedUrl = undefined;
    this.downloadUrl = undefined;
    this.selectedColors = [];
    this.file = undefined;
    this.file_uploading_sub = undefined;
  }

  ngOnInit(): void {
    this.setDefault();
  }

  ngOnDestroy() {
    this.file_uploading_sub.unsubscribe();
  }

  changeComplete($event: ColorEvent) {
    this.currentColor = $event.color.hex;
  }

  onSaveColor() {
    if (this.selectedColors.length < 16) {
      this.selectedColors.push(this.currentColor);
    }
  }

  onDeleteColor(color: any) {
    const index = this.selectedColors.indexOf(color);
    if (index > -1) {
      this.selectedColors.splice(index, 1);
    }
  }

  onFileDropped($event: any) {
    this.file = $event[0];
    this.showFile();

  }

  fileBrowseHandler($event: any) {
    this.file = $event.target.files[0];
    this.showFile();
  }

  onConvert() {
    this.converting = true;
    let params = new HttpParams();
    // @ts-ignore
    params = params.append('n', this.amountOfColors.toString());
    // @ts-ignore
    if (this.handMode) {
      for (let color of this.selectedColors) {
        params = params.append('centers', color);
      }
    }
    this.http.get(`${this.server}/image/reduce`,
      {
        responseType: 'blob',
        withCredentials: false,
        params: params
      })
      .subscribe(res => {
        this.downloadUrl = window.URL.createObjectURL(res);
        this.convertedUrl = this.dom.bypassSecurityTrustUrl(this.downloadUrl);
        this.converting = false;
      });
  }

  onDownload() {
    let a = document.createElement("a");
    a.href = this.downloadUrl;
    a.download = "converted.png";
    a.click();
  }

  onDeletePicture() {
    this.setDefault();
  }

  uploadFile() {
    if (this.file) {
      const formData = new FormData();
      formData.append(this.fileDropEl?.nativeElement.name, this.file);
      const upload = this.http.post(`${this.server}/image/upload`, formData,
        {
          withCredentials: false
        });
      this.file_uploading_sub = upload.subscribe(() => {
        this.uploaded = true;
      });
    }
  }

  showFile() {
    const mimeType = this.file.type;
    if (mimeType.match(/image\/*/) == null) {
      return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(this.file);
    reader.onload = (_event) => {
      this.url = reader.result;
      this.uploadFile();
    }
  }

  onSliderChange($event: any) {
    // @ts-ignore
    this.colorInp?.nativeElement.value = $event.value;
  }
}
