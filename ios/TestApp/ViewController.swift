//
//  ViewController.swift
//  GuessMySocialAg
//
//  Created by Michael Cheung on 1/16/16.
//  Copyright © 2016 i-connect. All rights reserved.
//

import UIKit
import FBSDKCoreKit
import FBSDKLoginKit

class ViewController: UIViewController, FBSDKLoginButtonDelegate
{
    var image:UIImage = UIImage()
    var userName = String()
    var apiJsonData = NSDictionary()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        if (FBSDKAccessToken.currentAccessToken() == nil){
            print("Not logged in..")
        }
        else{
            print("Logged in..")
        }
        
        //Create and show the Facebook login button
        let loginButton = FBSDKLoginButton()
        loginButton.readPermissions = ["public_profile", "email", "user_friends"]
        loginButton.center = self.view.center
        loginButton.delegate = self
        self.view.addSubview(loginButton)
        
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    // Send data to second view to display it
    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject?) {
        let destination = segue.destinationViewController as! AccountDetails
        destination.name = self.userName
        destination.age = "\(apiJsonData["social_age"])"
        destination.image = self.image
        destination.jsonData = self.apiJsonData
    }
    
    //Facebook login button
    func loginButton(loginButton: FBSDKLoginButton!, didCompleteWithResult result: FBSDKLoginManagerLoginResult!, error: NSError!) {
        if error == nil {
            print("Login complete")
            
            // Get user profile picture from Graph api
            let url = NSURL(string: "https://graph.facebook.com/me/picture?type=large&return_ssl_resources=1&access_token="+FBSDKAccessToken.currentAccessToken().tokenString)
            let urlRequest = NSURLRequest(URL: url!)
            let task2 = NSURLSession.sharedSession().dataTaskWithRequest(urlRequest){
                data, response, error in
                let image = UIImage(data: data!)
                self.image = image!
            }
            task2.resume()
            
            //Get user information from Graph API
            let graphRequest : FBSDKGraphRequest = FBSDKGraphRequest(graphPath: "me", parameters: nil)
            graphRequest.startWithCompletionHandler({ (connection, result, error) -> Void in
                if ((error) != nil)
                {
                    // Process error
                    print("Error: \(error)")
                }
                else
                {
                    let userName : NSString = result.valueForKey("name") as! NSString
                    self.userName = userName as String
                }
            })
            
            //POST request to our API
            var accesstokenData = "access_token=\(FBSDKAccessToken.currentAccessToken().tokenString)"
            let myUrl = NSURL(string: "http://murmuring-gorge-9791.herokuapp.com/fb_api/")
            let request = NSMutableURLRequest(URL: myUrl!)
            request.HTTPMethod = "POST"
            request.HTTPBody = accesstokenData.dataUsingEncoding(NSUTF8StringEncoding)
            
            let task = NSURLSession.sharedSession().dataTaskWithRequest(request){
                data, response, error in
                if error != nil {
                    print("error = \(error)")
                    return
                }
                
                //Fetch resulting JSON data from our API
                let responseString = NSString(data: data!, encoding: NSUTF8StringEncoding)
                do{
                    var json : NSDictionary? = nil
                    try json = NSJSONSerialization.JSONObjectWithData(data!, options: .MutableContainers) as? NSDictionary
                    if let parseJSON = json{
                        self.apiJsonData = parseJSON
                        //Finally switch to second view
                        self.performSegueWithIdentifier("showNew", sender: self)
                    }
                }
                catch{
                    print(error)
                    return
                }
                
            }
            task.resume()
        }
        else {
            print(error.localizedDescription)
        }
    }
    
    func loginButtonDidLogOut(loginButton: FBSDKLoginButton!) {
        print("User logged out...")
    }

}
