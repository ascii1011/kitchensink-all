package com.casualbacon.CBChart1;

import java.util.ArrayList;
import java.util.List;

import java.io.InputStream;
import java.net.URL;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.xml.sax.InputSource;
import org.xml.sax.XMLReader;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.webkit.WebView;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.Toast;
import android.widget.AdapterView.OnItemSelectedListener;

public class ChartsActivity extends Activity {
	
    Spinner spinner = null;
    //Spinner spinnerType = null; //added 10/2/2010
    WebView wvCharts = null;
    
    List<Books> Data = null;
    ArrayList<Location> locations = new ArrayList<Location>(); 
    
    ArrayAdapter <CharSequence> adapter = null;
    private DataHelper dh;
	public static final String KEY_TITLE = "name";
	public static final String KEY_ROWID = "_id";
	private static final String TAG = "MyActivity";
	
	protected int mPos;
    protected String mSelection;
    protected String mPath;

    String xmlOutput = "";
    
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.charts);     

        wvCharts = (WebView) findViewById(R.id.WebViewCharts);
        wvCharts.getSettings().setJavaScriptEnabled(true);
        spinner = (Spinner)findViewById(R.id.SpinnerCharts);
        //spinnerType = (Spinner)findViewById(R.id.SpinnerChartsType); //added 10/2/2010
        /*
         * added 
         * 	R.id.SpinnerChartsType &
         *  R.id.LinearLayoutChartsTypeNav
         *  10/2/2010 in res/layout/charts.xml
         */

        dh = new DataHelper(this); 

        //RecreateDB();

        adapter = new ArrayAdapter <CharSequence> (
        		this, android.R.layout.simple_spinner_item );
        adapter.setDropDownViewResource(
        		android.R.layout.simple_spinner_dropdown_item);

        //CreateSpinner cs = new CreateSpinner();
        Data = dh.selectAll_List();
        for (Books data : Data) {
			Log.v(TAG, "adding Book Data=" + data.getname());
       		adapter.add(data.getname());       		
        }
        spinner.setAdapter(adapter);        
        spinner.setOnItemSelectedListener(new MyOnItemSelectedListener());  
        
        /* 
         * added 10/2/2010
         * additionally added res/values/arrays.xml with a list of chart type codes...
         * referenced by R.array.planets_array below
         * 
         *  Note: will modify to use DB instead
         */
        //ArrayAdapter<CharSequence> adapterType = ArrayAdapter.createFromResource(
	    //        this, R.array.planets_array, android.R.layout.simple_spinner_item);
        //adapterType.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
	    //spinnerType.setAdapter(adapterType);
	    //spinnerType.setOnItemSelectedListener(new TypeListener());
        
    }
    
    public void RecreateDB() {
        this.dh.deleteAll();
        //this.dh.insert("google", "http://www.google.com");
        this.dh.insert("ascii", "http://www.asciiphilomath.com/graph2.xml"); 
    }
    /*
    public void CreateSpinner2() {

        dh = new DataHelper(this); 

        //RecreateDB();

        adapter = new ArrayAdapter <CharSequence> (
        		this, android.R.layout.simple_spinner_item );
        adapter.setDropDownViewResource(
        		android.R.layout.simple_spinner_dropdown_item);

        CreateSpinner cs = new CreateSpinner();
    }
    
    public class CreateSpinner {
    	
    	public CreateSpinner() {
	        Data = dh.selectAll_List();
	        for (Books data : Data) {
	       		adapter.add(data.getname());       		
	        }
	        spinner.setAdapter(adapter);
    	}
    }
    */
    

    /* 
     * added 10/2/2010
     * Not complete yet. 
     */
	//public class TypeListener implements OnItemSelectedListener {
		
		//@Override
	    //public void onItemSelected(AdapterView<?> parent,
	        //View view, int pos, long id) {

	    	//ChartsActivity.this.mPos = pos;
	    	//ChartsActivity.this.mSelection = parent.getItemAtPosition(pos).toString();
	    	//ChartsActivity.this.mPath = Data.get(pos).getpath();
	    	
	    	//Toast.makeText(parent.getContext(), 
	    	//	  "Navigating to (" + mSelection + ") " + mPath + ".",
	    	//	  Toast.LENGTH_SHORT).show();
	      
	      //if (isXML(mPath)) {
		//		Log.v(TAG, "mPath1=" + mPath);
		//		getUrl2XML(mPath);
	      //} else {
	    //	  	wvCharts.loadUrl(mPath);
	      //}
	    //}
		
		//@Override
	    //public void onNothingSelected(AdapterView parent) {
	      // Do nothing.
	    //}
	//}
    
    
    
    
    /*
     * On selecting a Title:
     * 	acquire selected info
     *  show a toast pop up briefly
     *  if the destination url has an xml ending then attempt to extract info from that file
     *  	then pull google chart site with xml info encoded into it.
     *  else if destination url is not a valid xml file then examine as regular site.
     */
	public class MyOnItemSelectedListener implements OnItemSelectedListener {
		
		//@Override
	    public void onItemSelected(AdapterView<?> parent,
	        View view, int pos, long id) {

	    	//acquire info
	    	ChartsActivity.this.mPos = pos;
	    	ChartsActivity.this.mSelection = parent.getItemAtPosition(pos).toString();
	    	ChartsActivity.this.mPath = Data.get(pos).getpath();
	    	
	    	//produce nav pop up showing destination url
	    	Toast.makeText(parent.getContext(), 
	    		  "Navigating to (" + mSelection + ") " + mPath + ".",
	    		  Toast.LENGTH_SHORT).show();
	      
	      if (isXML(mPath)) {
	    	  	//if url has a valid xml file extension
				Log.v(TAG, "mPath1=" + mPath);
				
				//process url path and nav to google charts with xml info
				getUrl2XML(mPath);
	      } else {
	    	  	//examine as regular site
	    	  	wvCharts.loadUrl(mPath);
	      }
	    }
		
		//@Override
	    public void onNothingSelected(AdapterView parent) {
	      // Do nothing.
	    }
	}
	
	public boolean isXML(String p) {
		
		if (p.toLowerCase().endsWith("xml")) {
			return true;
		}
		return false;
	}
		
	public void getUrl2XML(String Path) {

        UrlConnectionHelper connectionHelper = new UrlConnectionHelper();
        xmlOutput = connectionHelper.performGetRequest(Path);
        //Log.v(TAG, "xmlOutput=" + xmlOutput);
        

        parseXmlWithSax parser = new parseXmlWithSax();
        parser.parseXml(xmlOutput);
        locations = parser.getParseResult();

		/* Our ExampleHandler now provides the parsed data to us. */
		CreateGoogleGraphsUrl ggurl = new CreateGoogleGraphsUrl(
				locations.get(0).getChartType(),
				locations.get(0).getResolution(),
				locations.get(0).getData(),
				locations.get(0).getTags());


        wvCharts.getSettings().setJavaScriptEnabled(true);
		wvCharts.loadUrl(ggurl.getGGURL());
	}

	public void getWebView(String Path) {
		String surl = null;
		//String tmp = null;
		Log.v(TAG, "1=" + Path);
		
		//tmp = Path;
		try {

			Log.v(TAG, "2");
			/* Create a URL we want to load some xml-data from. */
			String url = "http://www.asciiphilomath.com/graph2.xml";
			InputStream stream = new java.net.URL(url).openStream(); 

			Log.v(TAG, "3");
			/* Get a SAXParser from the SAXPArserFactory. */
			SAXParserFactory spf = SAXParserFactory.newInstance();
			SAXParser sp = spf.newSAXParser();

			Log.v(TAG, "4");
			/* Get the XMLReader of the SAXParser we created. */
			XMLReader xr = sp.getXMLReader();

			Log.v(TAG, "5");
		/*  new graph parsing */
			GraphHandler myGraphHandler = new GraphHandler();
			xr.setContentHandler(myGraphHandler);

			Log.v(TAG, "6");
			/* Parse the xml-data from our URL. */
			xr.parse(new InputSource(stream));
			
			
			/* Parsing has finished. */

			Log.v(TAG, "7");
			/* Our ExampleHandler now provides the parsed data to us. */
			ParsedDirectDataSet parsedExampleDataSet = 
						myGraphHandler.getParsedData();	
			

			Log.v(TAG, "ChartType=" + parsedExampleDataSet.getChartType());
			Log.v(TAG, "getResolution=" + parsedExampleDataSet.getResolution());
			Log.v(TAG, "getData=" + parsedExampleDataSet.getData());
			Log.v(TAG, "getTags=" + parsedExampleDataSet.getTags());

			/* Our ExampleHandler now provides the parsed data to us. */
			CreateGoogleGraphsUrl ggurl = new CreateGoogleGraphsUrl(
					parsedExampleDataSet.getChartType(),
					parsedExampleDataSet.getResolution(),
					parsedExampleDataSet.getData(),
					parsedExampleDataSet.getTags());

			surl = ggurl.getGGURL();
			Log.v(TAG, "surl=" + surl);

			
		} catch (Exception e) {
			Log.v(TAG, "exception");
			surl = "";
		}

        wvCharts.getSettings().setJavaScriptEnabled(true);
		wvCharts.loadUrl(surl);
		//return surl;
	}
}
